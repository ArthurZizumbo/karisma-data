"""The catalog SQL against a real PostgreSQL, inside a rolled back transaction.

Skipped unless ``KARISMA_TEST_DATABASE_URL`` points at a database with the
catalog migration applied. Nothing here runs against SQLite: SQLite has no
``tsvector``, no ``to_tsquery`` and no generated column of that type, so a test
on it would measure an engine the product does not use.

The fixture inserts its own source and rolls the transaction back at the end,
so these cases neither need the seed of the catalog nor leave a trace in it.
Every search is scoped to that source, which is what lets the ranking cases
assert an order instead of a set.

The last case is different in kind: the Hit Rate@3 of the acceptance criteria
runs against the seeded catalog and the twenty queries frozen in
``tests/ml/data/consultas_referencia.json``, which this file reads and never
writes. Those queries come from the verbatims of A1 and A2 and were frozen
before the aliases were curated, which is the only reason the metric is not
circular.
"""

import asyncio
import json
import os
from collections.abc import AsyncIterator, Sequence
from pathlib import Path
from typing import Any, Final, cast

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import build_async_dsn
from app.models.catalog import CatalogSearchResponse
from app.services import catalog_service

VARIABLE: Final[str] = "KARISMA_TEST_DATABASE_URL"

# Source code of the fixture. It is not one of the twelve of the catalog, so
# these cases cannot pass by accidentally matching seeded content.
FUENTE: Final[str] = "sonda_us008"

# Frozen query set. Owned by the other wave of US-008: read here, never written.
CONSULTAS: Final[Path] = (
    Path(__file__).resolve().parents[1] / "ml" / "data" / "consultas_referencia.json"
)

# Below this many rows the catalog is not seeded and the metric would measure
# an empty table instead of the ranking.
MINIMO_DE_CAMPOS: Final[int] = 200

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
        'Riesgo de Credito', 'Ana Ruiz', 'CORE-SONDA', true)
"""

_CAMPO_SQL: Final[str] = """
INSERT INTO catalog_field (source_id, physical_name, business_name, definition,
                           aliases, domain, data_type, sensitivity,
                           refresh_frequency, certification, unit, metric_agg,
                           steward, valid_from, valid_to)
SELECT s.id, :physical_name, :business_name, :definition, :aliases, :domain,
       :data_type, :sensitivity, :refresh_frequency, :certification, :unit,
       :metric_agg, :steward, :valid_from, :valid_to
  FROM catalog_source s
 WHERE s.code = :source_code
"""

_NOTA_SQL: Final[str] = """
INSERT INTO catalog_tribal_note (field_id, note, applicability,
                                 applicability_terms, author, recorded_at)
SELECT f.id, :note, :applicability, :applicability_terms, :author, :recorded_at
  FROM catalog_field f
  JOIN catalog_source s ON s.id = f.source_id
 WHERE s.code = :source_code AND f.physical_name = :physical_name
"""

# Three entries chosen so that each case has something to separate. The
# definition of "dias de mora" carries the word "saldo" and its business name
# does not, which is the only way to see the A over C weighting.
_CAMPOS: Final[tuple[dict[str, object], ...]] = (
    {
        "physical_name": "sdo_cap",
        "business_name": "saldo de capital",
        "definition": "Monto insoluto del principal del credito a la fecha.",
        "aliases": "saldo insoluto outstanding principal balance",
        "domain": "cartera",
        "data_type": "decimal",
        "sensitivity": "interna",
        "refresh_frequency": "diaria",
        "certification": "certificado",
        "unit": "MXN",
        "metric_agg": "sum",
        "steward": None,
        "valid_from": "2021-01-01",
        "valid_to": None,
    },
    {
        "physical_name": "dias_mora",
        "business_name": "dias de mora",
        "definition": "Dias desde el primer saldo vencido no pagado del credito.",
        "aliases": "atraso days past due",
        "domain": "riesgo",
        "data_type": "entero",
        "sensitivity": "interna",
        "refresh_frequency": "diaria",
        "certification": "certificado",
        "unit": "dias",
        "metric_agg": "max",
        "steward": "Luis Mora",
        "valid_from": "2021-01-01",
        "valid_to": None,
    },
    {
        "physical_name": "sdo_ret",
        "business_name": "saldo retirado",
        "definition": "Definicion retirada, sustituida por el saldo de capital.",
        "aliases": "historico",
        "domain": "cartera",
        "data_type": "decimal",
        "sensitivity": "restringida",
        "refresh_frequency": "mensual",
        "certification": "obsoleto",
        "unit": "MXN",
        "metric_agg": "sum",
        "steward": None,
        "valid_from": "2019-01-01",
        "valid_to": "2020-12-31",
    },
)

_NOTAS: Final[tuple[dict[str, object], ...]] = (
    {
        "physical_name": "sdo_cap",
        "note": "El saldo se corta a las 23:00 hora local.",
        "applicability": "Aplica solo a posiciones de mercado local.",
        "applicability_terms": "fecha valor posicion local",
        "author": "Ana Ruiz",
        "recorded_at": "2025-11-04",
    },
    {
        "physical_name": "sdo_cap",
        "note": "Incluye los creditos reestructurados desde 2023.",
        "applicability": "Aplica siempre.",
        "applicability_terms": "",
        "author": "Luis Mora",
        "recorded_at": "2025-06-10",
    },
)


@pytest.fixture(scope="session")
def event_loop_policy() -> asyncio.AbstractEventLoopPolicy:
    """Return a loop policy psycopg can drive.

    On Windows the default is the proactor loop and psycopg refuses to run on
    it, so the whole module would fail on connect with a message that says
    nothing about the catalog.

    Returns:
        The selector policy on Windows, the default one elsewhere.
    """
    # The policy is looked up by name instead of behind a sys.platform test.
    # mypy narrows sys.platform to the platform running the check and declares
    # the other branch unreachable, so any form of that comparison fails the
    # lint on Windows and would fail it the other way round on a Linux runner.
    # Asking whether the class exists is also the more honest question: it is
    # defined only on Windows, which is exactly the condition that matters.
    politica_windows = getattr(asyncio, "WindowsSelectorEventLoopPolicy", None)
    if politica_windows is not None:
        return cast(asyncio.AbstractEventLoopPolicy, politica_windows())
    return asyncio.DefaultEventLoopPolicy()


@pytest_asyncio.fixture
async def sesion_sembrada() -> AsyncIterator[AsyncSession]:
    """Yield a session on the catalog exactly as the seed left it.

    The transaction is opened and rolled back even though nothing is written:
    it is what guarantees that a case which starts writing tomorrow cannot
    corrupt the seeded catalog of the developer machine.

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
async def sesion(sesion_sembrada: AsyncSession) -> AsyncSession:
    """Return the session with the fixture source of this module inserted.

    Args:
        sesion_sembrada: Session whose transaction is rolled back at the end.

    Returns:
        The same session, with three fields and two notes of its own.
    """
    connection = await sesion_sembrada.connection()
    await connection.execute(text(_FUENTE_SQL), {"code": FUENTE})
    for campo in _CAMPOS:
        await connection.execute(text(_CAMPO_SQL), {**campo, "source_code": FUENTE})
    for nota in _NOTAS:
        await connection.execute(text(_NOTA_SQL), {**nota, "source_code": FUENTE})
    return sesion_sembrada


async def _buscar(
    sesion: AsyncSession,
    consulta: str,
    *,
    only_current: bool = True,
    limit: int = catalog_service.DEFAULT_LIMIT,
    offset: int = catalog_service.DEFAULT_OFFSET,
) -> CatalogSearchResponse:
    """Search inside the fixture source.

    The optional arguments are spelled out instead of forwarded as ``**extra``:
    a kwargs bag types as ``Any``, which the lint rejects, and it also hides a
    typo in a keyword name behind a signature that accepts anything.

    Args:
        sesion: Session with the fixture catalog inserted.
        consulta: Free text of the search.
        only_current: When true, entries whose validity is already closed are
            excluded.
        limit: Page size.
        offset: Rows skipped before the page.

    Returns:
        The response payload.
    """
    return await catalog_service.search(
        sesion,
        raw_query=consulta,
        sources=[FUENTE],
        only_current=only_current,
        limit=limit,
        offset=offset,
    )


def _nombres(respuesta: CatalogSearchResponse) -> Sequence[str]:
    """Return the business names of a response, in order.

    Args:
        respuesta: Payload of a search.

    Returns:
        The business names, ranked.
    """
    return [hit.business_name for hit in respuesta.results]


@pytest.mark.asyncio
async def test_busqueda_con_acento_encuentra_lo_mismo_que_sin_acento(
    sesion: AsyncSession,
) -> None:
    """The Spanish configuration folds the accent, so both spellings agree.

    Swapping the configuration for ``simple`` would leave half the interface
    unable to find what it is looking for, and the failure is silent: the query
    succeeds and returns nothing.

    Args:
        sesion: Session with the fixture catalog inserted.
    """
    con = await _buscar(sesion, "crédito")
    sin = await _buscar(sesion, "credito")

    assert con.total > 0
    assert _nombres(con) == _nombres(sin)


@pytest.mark.asyncio
async def test_busqueda_en_plural_encuentra_el_singular(
    sesion: AsyncSession,
) -> None:
    """The plural finds the singular, which is what the stemmer is for.

    Replacing the tsvector with ``ILIKE`` "because with three hundred rows it
    is the same" breaks exactly here: people type in plural.

    Args:
        sesion: Session with the fixture catalog inserted.
    """
    respuesta = await _buscar(sesion, "saldos")

    assert "saldo de capital" in _nombres(respuesta)


@pytest.mark.asyncio
async def test_nombre_fisico_criptico_es_buscable(sesion: AsyncSession) -> None:
    """The physical name is indexed, so ``sdo_cap`` finds its entry.

    Dropping ``physical_name`` from the indexed document takes away the only
    way an analyst who knows the column can reach its definition.

    Args:
        sesion: Session with the fixture catalog inserted.
    """
    respuesta = await _buscar(sesion, "sdo_cap")

    assert _nombres(respuesta) == ["saldo de capital"]


@pytest.mark.asyncio
async def test_el_nombre_de_negocio_gana_a_la_definicion(
    sesion: AsyncSession,
) -> None:
    """A match in the business name ranks above a match in the definition.

    Both entries carry "saldo": one in its name, the other only in its prose.
    Losing the ``setweight`` calls makes the order arbitrary, and without an
    order the "@3" of the acceptance metric stops meaning anything.

    Args:
        sesion: Session with the fixture catalog inserted.
    """
    respuesta = await _buscar(sesion, "saldo")

    assert _nombres(respuesta) == ["saldo de capital", "dias de mora"]


@pytest.mark.asyncio
async def test_el_score_esta_acotado_entre_cero_y_uno(
    sesion: AsyncSession,
) -> None:
    """Every score falls in ``[0, 1)``, which is what the panel paints.

    Losing the normalisation flag 32 lets ``ts_rank`` return an unbounded
    number and any progress bar built on it goes off the rail.

    Args:
        sesion: Session with the fixture catalog inserted.
    """
    respuesta = await _buscar(sesion, "saldo credito mora")

    assert respuesta.results
    assert all(0.0 <= hit.score < 1.0 for hit in respuesta.results)


@pytest.mark.asyncio
async def test_nota_condicionada_solo_aparece_con_su_termino(
    sesion: AsyncSession,
) -> None:
    """The conditional note is attached by its trigger terms and not otherwise.

    Ignoring ``applicability_terms`` attaches every note to every query and
    reduces the Tk-Boost pattern to a free text field.

    Args:
        sesion: Session with the fixture catalog inserted.
    """
    sin_disparo = await _buscar(sesion, "sdo_cap")
    con_disparo = await _buscar(sesion, "sdo_cap fecha valor")

    assert [nota.attached_by for nota in sin_disparo.results[0].tribal_notes] == [
        "campo"
    ]
    assert sorted(nota.attached_by for nota in con_disparo.results[0].tribal_notes) == [
        "campo",
        "consulta",
    ]


@pytest.mark.asyncio
async def test_facet_counts_cuentan_el_conjunto_completo_y_no_la_pagina(
    sesion: AsyncSession,
) -> None:
    """The counts describe every match, even when the page shows one row.

    Counting over ``results`` makes the filter panel show "1" where there are
    three, which is worse than showing no count at all.

    Args:
        sesion: Session with the fixture catalog inserted.
    """
    respuesta = await _buscar(sesion, "saldo", only_current=False, limit=1)

    assert len(respuesta.results) == 1
    assert respuesta.total == 3
    assert respuesta.facet_counts["source"] == {FUENTE: 3}
    assert respuesta.facet_counts["certification"] == {
        "certificado": 2,
        "obsoleto": 1,
    }


@pytest.mark.asyncio
async def test_solo_vigentes_excluye_la_definicion_retirada(
    sesion: AsyncSession,
) -> None:
    """A retired definition is out by default and in when it is asked for.

    Without ``valid_to`` in the predicate the catalog cannot represent a
    withdrawn field, which is the case that makes a catalog believable.

    Args:
        sesion: Session with the fixture catalog inserted.
    """
    vigentes = await _buscar(sesion, "saldo")
    todas = await _buscar(sesion, "saldo", only_current=False)

    assert "saldo retirado" not in _nombres(vigentes)
    assert "saldo retirado" in _nombres(todas)
    retirada = next(
        hit for hit in todas.results if hit.business_name == "saldo retirado"
    )
    assert retirada.validity.is_current is False
    assert retirada.validity.valid_to is not None


@pytest.mark.asyncio
async def test_la_ficha_recupera_la_entrada_por_su_identificador(
    sesion: AsyncSession,
) -> None:
    """The detail endpoint reads the same row the search ranked.

    The steward of ``sdo_cap`` is null on purpose: the fallback to the owner of
    the source is resolved by the backend, and this is where a client side
    coalesce would show up as an empty name.

    Args:
        sesion: Session with the fixture catalog inserted.
    """
    respuesta = await _buscar(sesion, "sdo_cap")
    ficha = await catalog_service.get_entry(sesion, respuesta.results[0].field_id)

    assert ficha is not None
    assert ficha.physical_name == "sdo_cap"
    assert ficha.owner.steward == "Ana Ruiz"
    assert ficha.source.code == FUENTE
    assert await catalog_service.get_entry(sesion, 10**9) is None


@pytest.mark.asyncio
async def test_hit_rate_at_3(sesion_sembrada: AsyncSession) -> None:
    """The twenty frozen queries find their source among the first three hits.

    This is the acceptance metric of the US and the only case here that reads
    the seeded catalog. It fails when the ranking breaks, when an alias is
    dropped, or when a definition stops carrying the words people actually
    type. The queries were frozen before the aliases were curated, so raising
    the number by editing a query is forbidden: the only allowed repair is
    adding a synonym a person would really say.

    Args:
        sesion_sembrada: Session on the catalog as the seed left it.
    """
    conexion = await sesion_sembrada.connection()
    resultado = await conexion.execute(
        text("SELECT count(*) AS total FROM catalog_field")
    )
    fila = resultado.mappings().one()
    assert int(fila["total"]) >= MINIMO_DE_CAMPOS, (
        "aplica el seed del catalogo con 'make db-seed' antes de medir el Hit Rate@3"
    )

    datos: dict[str, Any] = json.loads(CONSULTAS.read_text(encoding="utf-8"))
    consultas: list[dict[str, Any]] = datos["queries"]
    fallidas: list[str] = []
    for caso in consultas:
        respuesta = await catalog_service.search(
            sesion_sembrada, raw_query=caso["query"], limit=datos["hit_rate_at"]
        )
        fuentes = {hit.source.code for hit in respuesta.results}
        if caso["expected_source"] not in fuentes:
            fallidas.append(f"{caso['id']}. {caso['query']} -> {sorted(fuentes)}")

    aciertos = len(consultas) - len(fallidas)
    hit_rate = aciertos / len(consultas)
    assert hit_rate >= datos["gate"], (
        f"Hit Rate@{datos['hit_rate_at']} = {hit_rate} "
        f"({aciertos}/{len(consultas)}); fallaron: {fallidas}"
    )
