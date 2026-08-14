"""The third migration of the project, read as versioned text.

``tests/backend/test_migraciones.py`` already walks every file of the directory
and checks the name pattern, the two dbmate sections and their order, so nothing
of that is repeated here: a case that cannot fail on its own is not a case. What
this module asserts is what is specific to ``add_app_user_updated_at`` and would
otherwise only be discovered against a live database.

No connection is opened. The files read are the ones git tracks, which is the
same discipline the migration suite of US-002 established: inspecting a running
PostgreSQL would prove the state of one machine, not the contract of the
repository.
"""

import re
from pathlib import Path
from typing import Final

import pytest

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[3]
MIGRATIONS_DIR: Final[Path] = REPO_ROOT / "db" / "migrations"
SCHEMA_FILE: Final[Path] = REPO_ROOT / "db" / "schema.sql"

SLUG: Final[str] = "add_app_user_updated_at"

UP_MARKER: Final[str] = "-- migrate:up"
DOWN_MARKER: Final[str] = "-- migrate:down"


@pytest.fixture(scope="module")
def migracion() -> Path:
    """Return the single migration that adds the modification stamp.

    Returns:
        The path of the migration file.
    """
    coincidencias = sorted(MIGRATIONS_DIR.glob(f"*_{SLUG}.sql"))
    assert len(coincidencias) == 1, (
        f"se esperaba exactamente una migracion *_{SLUG}.sql, "
        f"se encontraron {len(coincidencias)}"
    )
    return coincidencias[0]


@pytest.fixture(scope="module")
def secciones(migracion: Path) -> tuple[str, str]:
    """Split the migration into its up and down sections.

    Args:
        migracion: Path of the migration file.

    Returns:
        The text of the up section and the text of the down section.
    """
    sql = migracion.read_text(encoding="utf-8")
    cuerpo = sql.split(UP_MARKER, 1)[1]
    subida, bajada = cuerpo.split(DOWN_MARKER, 1)
    return subida, bajada


def test_la_columna_se_anade_no_nula_y_con_valor_por_defecto(
    secciones: tuple[str, str],
) -> None:
    """The column arrives ``NOT NULL`` with a default, so the seven rows survive.

    Adding it nullable would leave the interface reading an empty modification
    date for every account and would push the decision to the client; adding it
    ``NOT NULL`` without a default fails on a table that already has rows.
    """
    subida = secciones[0]

    assert re.search(
        r"ADD\s+COLUMN\s+updated_at\s+TIMESTAMPTZ\s+NOT\s+NULL\s+DEFAULT\s+now\(\)",
        subida,
        re.IGNORECASE,
    )


def test_las_filas_sembradas_se_igualan_a_su_creacion(
    secciones: tuple[str, str],
) -> None:
    """An account nobody has touched must not read as modified today.

    Without this statement the seven seeded users would all show the date of the
    migration, and the only audit trail this screen has would open its life with
    seven false modifications.
    """
    subida = secciones[0]

    assert re.search(
        r"UPDATE\s+app_user\s+SET\s+updated_at\s*=\s*created_at",
        subida,
        re.IGNORECASE,
    )


def test_la_reversa_devuelve_la_tabla_a_su_estado_anterior(
    secciones: tuple[str, str],
) -> None:
    """The down section really drops the column instead of being a comment."""
    bajada = secciones[1]

    assert re.search(
        r"ALTER\s+TABLE\s+app_user\s+DROP\s+COLUMN\s+updated_at",
        bajada,
        re.IGNORECASE,
    )


def test_no_se_instala_disparador_ni_indice(migracion: Path) -> None:
    """The stamp is written by the service, in the open, and nothing indexes it.

    A trigger would make invisible in the code what happens in the database, and
    would silently keep working if the explicit write of the repository were
    removed; an index over a column no query filters or sorts by is weight that
    also has to be reverted.
    """
    sql = migracion.read_text(encoding="utf-8").upper()

    assert "CREATE TRIGGER" not in sql
    assert "CREATE INDEX" not in sql


def test_el_volcado_versionado_ya_trae_la_columna_y_la_version(
    migracion: Path,
) -> None:
    """``db/schema.sql`` was regenerated, so nobody deploys a different schema.

    Committing the migration without running ``make db-up`` leaves the versioned
    dump describing a table that no longer exists, and the next reader trusts
    the dump.
    """
    volcado = SCHEMA_FILE.read_text(encoding="utf-8")
    version = migracion.name.split("_", 1)[0]

    definicion = volcado.split("CREATE TABLE public.app_user (", 1)[1].split(");", 1)[0]
    assert "updated_at timestamp with time zone DEFAULT now() NOT NULL" in definicion
    assert f"('{version}')" in volcado


def test_la_migracion_es_ascii_sin_diacriticos(migracion: Path) -> None:
    """Everything that ends up in the dump stays ASCII, as ``db/AGENTS.md`` asks.

    A comment with an accent travels into ``schema.sql`` through
    ``COMMENT ON COLUMN`` and turns the diff of the dump into noise the day
    somebody regenerates it with another locale.
    """
    crudo = migracion.read_bytes()

    assert crudo.decode("ascii", errors="ignore").encode("ascii") == crudo
