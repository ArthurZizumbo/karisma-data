"""The lineage schema and its seed against a real PostgreSQL.

Skipped unless ``KARISMA_TEST_DATABASE_URL`` points at a database with the
migrations applied. Nothing here runs against SQLite: what is measured is a
``CHECK``, a unique index and a cascading foreign key, and SQLite enforces
none of the three the way PostgreSQL does.

Every case opens a transaction and rolls it back, so the ones that write -a
duplicated order, a truncated catalog- neither need the seed to be reapplied
nor leave a trace in it.
"""

import asyncio
import os
import re
from collections.abc import AsyncIterator
from typing import Any, Final, cast

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import build_async_dsn
from app.models.lineage import (
    FIELD_PUBLISH_CODE,
    LINEAGE_TRANSFORMATION_CODES,
    LineageStage,
)
from app.services import lineage_service

VARIABLE: Final[str] = "KARISMA_TEST_DATABASE_URL"

#: Rows the curated seed writes: twelve sources times four stored hops.
PASOS_SEMBRADOS: Final[int] = 48
FUENTES_SEMBRADAS: Final[int] = 12
PASOS_POR_FUENTE: Final[int] = 4

#: Source code of the fixture. It is not one of the twelve of the catalog, so
#: these cases cannot pass by accidentally matching seeded content.
FUENTE: Final[str] = "sonda_us029"

pytestmark = [
    pytest.mark.integracion,
    pytest.mark.skipif(
        not os.environ.get(VARIABLE),
        reason=f"define {VARIABLE} para ejecutar las pruebas de integracion",
    ),
]

_FUENTE_SQL: Final[str] = """
INSERT INTO catalog_source (code, display_name, description, owner_area,
                            owner_name, system_of_record, has_extract)
VALUES (:code, 'Fuente de sonda', 'Fuente efimera de la prueba de integracion',
        'Riesgo de Credito', 'Ana Ruiz', 'CORE-SONDA', false)
"""

_CAMPO_SQL: Final[str] = """
INSERT INTO catalog_field (source_id, physical_name, business_name, definition,
                           aliases, domain, data_type, sensitivity,
                           refresh_frequency, certification, unit, metric_agg,
                           steward, valid_from, valid_to)
SELECT s.id, 'sdo_sonda', 'saldo de sonda', 'Campo efimero de la prueba.',
       'sonda', 'cartera', 'decimal', 'interna', 'diaria', 'certificado',
       'MXN', 'sum', NULL, DATE '2021-01-01', NULL
  FROM catalog_source s
 WHERE s.code = :code
RETURNING id
"""

_PASO_SQL: Final[str] = """
INSERT INTO catalog_lineage_step (source_id, step_order, stage, system_code,
                                  system_name, transformation_code,
                                  transformation_detail, owner_area, owner_name,
                                  effective_from, effective_to)
SELECT s.id, :step_order, :stage, 'CORE-SONDA', 'Sistema de sonda',
       :transformation_code, :transformation_detail, 'Plataforma de Datos',
       :owner_name, DATE '2022-01-01', NULL
  FROM catalog_source s
 WHERE s.code = :code
"""

# Inserted backwards on purpose: the identifiers grow in the opposite order to
# the journey, which is the only way a service that sorted by ``id`` would show
# the quality control first and still look correct.
_PASOS_INVERTIDOS: Final[tuple[dict[str, Any], ...]] = (
    {
        "step_order": 4,
        "stage": LineageStage.CALIDAD.value,
        "transformation_code": "quality_rule",
        "transformation_detail": "ctrl_sonda",
        "owner_name": "Teresa Villalba",
    },
    {
        "step_order": 3,
        "stage": LineageStage.TRANSFORMACION.value,
        "transformation_code": "business_rule",
        "transformation_detail": "regla_sonda",
        "owner_name": "Sofia Aranda",
    },
    {
        "step_order": 2,
        "stage": LineageStage.EXTRACCION.value,
        "transformation_code": "batch_extract",
        "transformation_detail": "job_sonda",
        "owner_name": "Emilio Cazares",
    },
    {
        "step_order": 1,
        "stage": LineageStage.ORIGEN.value,
        "transformation_code": "origin_capture",
        "transformation_detail": "CORE-SONDA.TABLA",
        "owner_name": "Alberto Nunez",
    },
)


@pytest.fixture(scope="session")
def event_loop_policy() -> asyncio.AbstractEventLoopPolicy:
    """Return a loop policy psycopg can drive.

    On Windows the default is the proactor loop and psycopg refuses to run on
    it, so the whole module would fail on connect with a message that says
    nothing about the lineage.

    Returns:
        The selector policy on Windows, the default one elsewhere.
    """
    # Looked up by name and not behind a sys.platform test: mypy narrows
    # sys.platform to the platform running the check and declares the other
    # branch unreachable, so any form of that comparison fails the lint on one
    # operating system or the other.
    politica_windows = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
    if politica_windows is not None:
        return cast(asyncio.AbstractEventLoopPolicy, politica_windows())
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture
async def sesion_sembrada() -> AsyncIterator[AsyncSession]:
    """Yield a session on the catalog exactly as the seed left it.

    The transaction is rolled back at the end, which is what lets the cases
    that write -a duplicated order, a truncated catalog- run against the
    developer database without corrupting it.

    Yields:
        A session bound to a connection whose transaction is never committed.
    """
    engine = create_async_engine(build_async_dsn(os.environ[VARIABLE]))
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            abierta = AsyncSession(bind=connection, expire_on_commit=False)
            try:
                yield abierta
            finally:
                await abierta.close()
                await transaction.rollback()
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def sesion_con_sonda(sesion_sembrada: AsyncSession) -> AsyncSession:
    """Return the session with the fixture source, field and hops inserted.

    Args:
        sesion_sembrada: Session whose transaction is rolled back at the end.

    Returns:
        The same session, carrying one source of its own with four hops whose
        identifiers grow backwards.
    """
    connection = await sesion_sembrada.connection()
    await connection.execute(text(_FUENTE_SQL), {"code": FUENTE})
    await connection.execute(text(_CAMPO_SQL), {"code": FUENTE})
    for paso in _PASOS_INVERTIDOS:
        await connection.execute(text(_PASO_SQL), {**paso, "code": FUENTE})
    return sesion_sembrada


async def _escalar(sesion: AsyncSession, statement: str, **params: object) -> object:
    """Run a statement and return the first column of its first row.

    Args:
        sesion: Session bound to the rolled back transaction.
        statement: SQL to run.
        **params: Bind parameters.

    Returns:
        The scalar the statement selected.
    """
    connection = await sesion.connection()
    resultado = await connection.execute(text(statement), params)
    return resultado.scalar()


async def _entero(sesion: AsyncSession, statement: str, **params: object) -> int:
    """Run a counting statement and return its result.

    Args:
        sesion: Session bound to the rolled back transaction.
        statement: SQL to run.
        **params: Bind parameters.

    Returns:
        The count. The narrowing is asserted and not cast, so a statement that
        stops counting fails here instead of three lines later.
    """
    valor = await _escalar(sesion, statement, **params)
    assert isinstance(valor, int)
    return valor


async def _id_del_campo(sesion: AsyncSession) -> int:
    """Return the identifier of the field of the fixture source.

    Args:
        sesion: Session with the fixture source inserted.

    Returns:
        The primary key of the ephemeral catalog entry.
    """
    return await _entero(
        sesion,
        "SELECT f.id FROM catalog_field f"
        "  JOIN catalog_source s ON s.id = f.source_id"
        " WHERE s.code = :code",
        code=FUENTE,
    )


@pytest.mark.asyncio
async def test_el_check_de_la_base_nombra_los_mismos_codigos_que_python(
    sesion_sembrada: AsyncSession,
) -> None:
    """The closed vocabulary is one, written twice, and the two copies agree.

    A code added to the constant without a migration -or to the migration
    without the constant- would seed cleanly and reach the interface as a key
    with no template, printed on screen as a dotted string in both languages.

    Args:
        sesion_sembrada: Session on the migrated database.
    """
    definicion = await _escalar(
        sesion_sembrada,
        "SELECT pg_get_constraintdef(oid) FROM pg_constraint"
        " WHERE conname = 'catalog_lineage_step_transformation_code_check'",
    )

    codigos = tuple(re.findall(r"'([a-z_]+)'::text", str(definicion)))

    assert codigos == LINEAGE_TRANSFORMATION_CODES
    assert FIELD_PUBLISH_CODE not in codigos


@pytest.mark.asyncio
async def test_la_etapa_de_presentacion_no_se_puede_sembrar(
    sesion_con_sonda: AsyncSession,
) -> None:
    """The derived stage is rejected by the database, not just by convention.

    Widening the ``CHECK`` to admit it is how the terminal hop ends up stored:
    a second truth for a fact ``catalog_field`` already owns, which no test
    would catch afterwards because both copies would look right on the day.

    Args:
        sesion_con_sonda: Session with the fixture source inserted.
    """
    connection = await sesion_con_sonda.connection()

    with pytest.raises(IntegrityError):
        await connection.execute(
            text(_PASO_SQL),
            {
                "code": FUENTE,
                "step_order": 5,
                "stage": LineageStage.PRESENTACION.value,
                "transformation_code": "quality_rule",
                "transformation_detail": "ctrl_sonda",
                "owner_name": "Teresa Villalba",
            },
        )


@pytest.mark.asyncio
async def test_el_indice_unico_impide_dos_pasos_con_el_mismo_orden(
    sesion_con_sonda: AsyncSession,
) -> None:
    """No source can carry two hops numbered the same.

    Without the unique index the journey would come back with two third steps
    and no fourth, in an order the planner decides, and the overlay would paint
    a different sequence on every request.

    Args:
        sesion_con_sonda: Session with the fixture source and its four hops.
    """
    connection = await sesion_con_sonda.connection()

    with pytest.raises(IntegrityError):
        await connection.execute(
            text(_PASO_SQL),
            {
                "code": FUENTE,
                "step_order": 3,
                "stage": LineageStage.TRANSFORMACION.value,
                "transformation_code": "deduplication",
                "transformation_detail": "regla_repetida",
                "owner_name": "Sofia Aranda",
            },
        )


@pytest.mark.asyncio
async def test_truncar_el_catalogo_arrastra_el_linaje(
    sesion_con_sonda: AsyncSession,
) -> None:
    """The seed of US-008 must keep working with this table in the schema.

    ``db/seeds/catalog.sql`` opens with ``TRUNCATE ... CASCADE`` over
    ``catalog_source``. A foreign key without ``ON DELETE CASCADE`` makes that
    statement fail and leaves ``make db-seed`` broken for the whole team, which
    is a defect nobody would attribute to the lineage.

    Args:
        sesion_con_sonda: Session with the fixture source and its four hops.
    """
    connection = await sesion_con_sonda.connection()

    await connection.execute(
        text(
            "TRUNCATE catalog_tribal_note, catalog_field, catalog_source"
            " RESTART IDENTITY CASCADE"
        )
    )

    restantes = await _entero(
        sesion_con_sonda, "SELECT count(*) FROM catalog_lineage_step"
    )

    assert restantes == 0


@pytest.mark.asyncio
async def test_el_servicio_recorre_por_orden_de_paso_y_no_por_identificador(
    sesion_con_sonda: AsyncSession,
) -> None:
    """The journey is read in the order of the work, not of the insertion.

    The four hops of the fixture were inserted backwards, so a service that
    sorted by ``id`` -or that did not sort at all- would open the panel at the
    quality control and end at the capture, and every sentence of the overlay
    would still be true one by one.

    Args:
        sesion_con_sonda: Session with the fixture source and its four hops.
    """
    linaje = await lineage_service.get_field_lineage(
        sesion_con_sonda, entry_id=await _id_del_campo(sesion_con_sonda)
    )

    assert [paso.stage for paso in linaje.steps] == [
        LineageStage.ORIGEN,
        LineageStage.EXTRACCION,
        LineageStage.TRANSFORMACION,
        LineageStage.CALIDAD,
        LineageStage.PRESENTACION,
    ]
    assert [paso.stored for paso in linaje.steps] == [True, True, True, True, False]
    assert linaje.steps[-1].transformation_detail == "sdo_sonda"


@pytest.mark.asyncio
async def test_toda_fuente_sembrada_tiene_sus_cuatro_pasos(
    sesion_sembrada: AsyncSession,
) -> None:
    """The curated seed covers the twelve sources, four hops each.

    The seed finds its source with a join on the natural code, so a renamed
    code drops its four rows IN SILENCE. This is the case that turns that
    silence into a failure: a source with no hops would open an overlay showing
    the derived step alone, with nothing to say where the figure came from.

    Args:
        sesion_sembrada: Session on the seeded database.
    """
    fuentes = await _entero(sesion_sembrada, "SELECT count(*) FROM catalog_source")
    if fuentes == 0:
        pytest.skip("catalogo sin sembrar: aplica make db-seed")

    total = await _entero(sesion_sembrada, "SELECT count(*) FROM catalog_lineage_step")
    con_pasos = await _entero(
        sesion_sembrada,
        "SELECT count(*) FROM catalog_source s"
        " WHERE (SELECT count(*) FROM catalog_lineage_step l"
        "         WHERE l.source_id = s.id) = :esperados",
        esperados=PASOS_POR_FUENTE,
    )

    assert fuentes == FUENTES_SEMBRADAS
    assert total == PASOS_SEMBRADOS
    assert con_pasos == FUENTES_SEMBRADAS


@pytest.mark.asyncio
async def test_cada_fuente_sembrada_recorre_las_cuatro_etapas_una_vez(
    sesion_sembrada: AsyncSession,
) -> None:
    """No source repeats a stage or skips one.

    Four rows per source is not enough: a seed with two extractions and no
    quality control would count the same and would tell the reader that nobody
    checks the figure.

    Args:
        sesion_sembrada: Session on the seeded database.
    """
    if await _entero(sesion_sembrada, "SELECT count(*) FROM catalog_source") == 0:
        pytest.skip("catalogo sin sembrar: aplica make db-seed")

    desordenadas = await _entero(
        sesion_sembrada,
        "SELECT count(*) FROM ("
        "  SELECT source_id FROM catalog_lineage_step"
        "   GROUP BY source_id"
        "  HAVING array_agg(stage ORDER BY step_order) <> :esperadas"
        ") AS fuera_de_orden",
        esperadas=[
            LineageStage.ORIGEN.value,
            LineageStage.EXTRACCION.value,
            LineageStage.TRANSFORMACION.value,
            LineageStage.CALIDAD.value,
        ],
    )

    assert desordenadas == 0
