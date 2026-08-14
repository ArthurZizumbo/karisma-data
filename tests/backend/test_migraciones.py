"""Contract tests for the dbmate migration directory and the versioned schema.

US-002 ships the migration mechanism, not the domain schema: the only file in
``db/migrations/`` today enables the ``vector`` extension. The assertions below
encode the rules of ``db/AGENTS.md`` over versioned text files, so they keep
serving unchanged when the four canonical migrations land: every migration
declares ``-- migrate:up`` and ``-- migrate:down``, and ``db/schema.sql``
records what was applied.

No test here opens a PostgreSQL connection nor starts Docker. The suite reads
files tracked by git and nothing else: inspecting a live database would prove
the state of one machine, not the contract of the repository.
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "db" / "migrations"
SCHEMA_FILE = REPO_ROOT / "db" / "schema.sql"

UP_MARKER = "-- migrate:up"
DOWN_MARKER = "-- migrate:down"

FILE_NAME_PATTERN = re.compile(r"^(\d{14})_[a-z0-9]+(?:_[a-z0-9]+)*\.sql$")
CREATE_VECTOR_PATTERN = re.compile(
    r"CREATE\s+EXTENSION\s+IF\s+NOT\s+EXISTS\s+vector",
    re.IGNORECASE,
)
DROP_VECTOR_PATTERN = re.compile(
    r"DROP\s+EXTENSION\s+IF\s+EXISTS\s+vector",
    re.IGNORECASE,
)

PGVECTOR_MIGRATION = "20260811005732_enable_pgvector_extension.sql"

MIGRATIONS: list[Path] = sorted(MIGRATIONS_DIR.glob("*.sql"))
MIGRATION_IDS: list[str] = [path.name for path in MIGRATIONS]


def read_sql(path: Path) -> str:
    """Return the decoded content of a migration file.

    Args:
        path: Absolute path of the ``.sql`` file.

    Returns:
        The file content decoded as UTF-8.
    """
    return path.read_text(encoding="utf-8")


def count_marker(sql: str, marker: str) -> int:
    """Count the lines that are exactly a dbmate section marker.

    Args:
        sql: Full content of a migration file.
        marker: Marker to count, ``-- migrate:up`` or ``-- migrate:down``.

    Returns:
        The number of lines whose stripped content equals the marker.
    """
    return sum(1 for line in sql.splitlines() if line.strip() == marker)


def marker_index(sql: str, marker: str) -> int:
    """Return the zero-based line index of a section marker.

    Args:
        sql: Full content of a migration file.
        marker: Marker to locate.

    Returns:
        The index of the first matching line, or ``-1`` when the marker is
        absent.
    """
    for index, line in enumerate(sql.splitlines()):
        if line.strip() == marker:
            return index
    return -1


def section_body(sql: str, marker: str) -> str:
    """Return the SQL that follows a section marker.

    The body ends at the next section marker, or at the end of the file for
    the last section.

    Args:
        sql: Full content of a migration file.
        marker: Marker that opens the section.

    Returns:
        The raw text of the section, empty when the marker is absent.
    """
    start = marker_index(sql, marker)
    if start < 0:
        return ""
    body: list[str] = []
    for line in sql.splitlines()[start + 1 :]:
        if line.strip() in (UP_MARKER, DOWN_MARKER):
            break
        body.append(line)
    return "\n".join(body)


def statements(body: str) -> list[str]:
    """Split a section body into executable statements.

    Comment lines are dropped first, so a section that is documented but not
    implemented is reported as empty instead of passing on its prose.

    Args:
        body: Raw text of a migration section.

    Returns:
        The list of non-empty statements, each without its trailing semicolon.
    """
    code = "\n".join(
        line for line in body.splitlines() if not line.strip().startswith("--")
    )
    return [chunk.strip() for chunk in code.split(";") if chunk.strip()]


def test_directorio_de_migraciones_tiene_contenido() -> None:
    """The directory holds at least one migration.

    This guard exists so that the parametrized cases below can never pass by
    iterating over an empty list.
    """
    assert MIGRATIONS_DIR.is_dir(), "Falta el directorio db/migrations/"
    assert MIGRATIONS, "db/migrations/ esta vacio: dbmate no tendria que aplicar"


@pytest.mark.parametrize("migration", MIGRATIONS, ids=MIGRATION_IDS)
def test_nombre_de_migracion_sigue_la_convencion(migration: Path) -> None:
    """Check the name is a 14-digit timestamp followed by a snake_case slug.

    Args:
        migration: Migration file under inspection.
    """
    assert FILE_NAME_PATTERN.match(migration.name), (
        f"{migration.name} no sigue el formato <timestamp>_<slug>.sql de dbmate"
    )


@pytest.mark.parametrize("migration", MIGRATIONS, ids=MIGRATION_IDS)
def test_migracion_declara_ambas_secciones(migration: Path) -> None:
    """Every migration declares exactly one up section and one down section.

    Args:
        migration: Migration file under inspection.
    """
    sql = read_sql(migration)

    assert count_marker(sql, UP_MARKER) == 1, (
        f"{migration.name} debe declarar exactamente una seccion {UP_MARKER}"
    )
    assert count_marker(sql, DOWN_MARKER) == 1, (
        f"{migration.name} debe declarar exactamente una seccion "
        f"{DOWN_MARKER}: toda migracion es reversible"
    )


@pytest.mark.parametrize("migration", MIGRATIONS, ids=MIGRATION_IDS)
def test_migracion_ordena_up_antes_de_down(migration: Path) -> None:
    """The up section precedes the down section, as dbmate expects.

    Args:
        migration: Migration file under inspection.
    """
    sql = read_sql(migration)

    assert marker_index(sql, UP_MARKER) < marker_index(sql, DOWN_MARKER), (
        f"{migration.name} declara el rollback antes que la aplicacion"
    )


@pytest.mark.parametrize("migration", MIGRATIONS, ids=MIGRATION_IDS)
def test_migracion_tiene_sentencias_en_ambas_secciones(migration: Path) -> None:
    """Neither section is an empty shell made only of comments.

    Args:
        migration: Migration file under inspection.
    """
    sql = read_sql(migration)

    assert statements(section_body(sql, UP_MARKER)), (
        f"{migration.name} no ejecuta ninguna sentencia en {UP_MARKER}"
    )
    assert statements(section_body(sql, DOWN_MARKER)), (
        f"{migration.name} no revierte nada en {DOWN_MARKER}: "
        "un rollback vacio no es un rollback"
    )


def test_versiones_de_migracion_son_unicas() -> None:
    """No two migrations share the same 14-digit version.

    dbmate keys ``schema_migrations`` by that prefix: a collision would leave
    the second migration silently unapplied.
    """
    versions = [migration.name[:14] for migration in MIGRATIONS]

    assert len(versions) == len(set(versions)), (
        f"Hay versiones de migracion repetidas en db/migrations/: {versions}"
    )


def test_schema_versionado_existe() -> None:
    """The dump exists and carries the bookkeeping table written by dbmate."""
    assert SCHEMA_FILE.is_file(), "Falta db/schema.sql, el volcado versionado"

    schema = SCHEMA_FILE.read_text(encoding="utf-8")

    assert "public.schema_migrations" in schema, (
        "db/schema.sql no declara schema_migrations: no lo genero dbmate"
    )


@pytest.mark.parametrize("migration", MIGRATIONS, ids=MIGRATION_IDS)
def test_schema_registra_cada_migracion_aplicada(migration: Path) -> None:
    """The dump records the version of every migration of the directory.

    ``db/AGENTS.md`` requires ``schema.sql`` in the same commit as the
    migration; a version missing here means the dump went stale.

    Args:
        migration: Migration file under inspection.
    """
    schema = SCHEMA_FILE.read_text(encoding="utf-8")
    version = migration.name[:14]

    assert f"('{version}')" in schema, (
        f"db/schema.sql no registra la version {version}: "
        "regenera el volcado con make db-up antes de commitear"
    )


def test_migracion_pgvector_existe() -> None:
    """The pgvector migration of US-002 is present with its exact name."""
    assert (MIGRATIONS_DIR / PGVECTOR_MIGRATION).is_file(), (
        f"Falta db/migrations/{PGVECTOR_MIGRATION}"
    )


def test_pgvector_habilita_la_extension_de_forma_idempotente() -> None:
    """The up creates the extension guarded by ``IF NOT EXISTS``.

    The compose image may already carry the extension enabled, so a plain
    ``CREATE EXTENSION`` would abort the very first ``dbmate up``.
    """
    sql = read_sql(MIGRATIONS_DIR / PGVECTOR_MIGRATION)
    up_body = section_body(sql, UP_MARKER)

    assert CREATE_VECTOR_PATTERN.search(up_body), (
        "El up debe ejecutar CREATE EXTENSION IF NOT EXISTS vector"
    )


def test_pgvector_revierte_la_extension_de_forma_tolerante() -> None:
    """The down drops the extension guarded by ``IF EXISTS``.

    A rollback that fails because the object is already gone is a rollback
    nobody dares to run.
    """
    sql = read_sql(MIGRATIONS_DIR / PGVECTOR_MIGRATION)
    down_body = section_body(sql, DOWN_MARKER)

    assert DROP_VECTOR_PATTERN.search(down_body), (
        "El down debe ejecutar DROP EXTENSION IF EXISTS vector"
    )


def test_pgvector_solo_toca_la_extension() -> None:
    """The migration stays infrastructure: one statement, no domain tables.

    Freezing ``catalog_field`` here would force editing an applied migration
    once the catalog is designed, which ``db/AGENTS.md`` forbids.
    """
    sql = read_sql(MIGRATIONS_DIR / PGVECTOR_MIGRATION)
    up_statements = statements(section_body(sql, UP_MARKER))

    assert len(up_statements) == 1, (
        f"El up debe tener una sola sentencia, tiene {len(up_statements)}"
    )
    assert "CREATE TABLE" not in sql.upper(), (
        "Esta migracion es infraestructura: no crea tablas de dominio"
    )


def test_schema_refleja_la_extension_vector() -> None:
    """The versioned dump proves the extension was actually applied."""
    schema = SCHEMA_FILE.read_text(encoding="utf-8")

    assert CREATE_VECTOR_PATTERN.search(schema), (
        "db/schema.sql no refleja la extension vector aplicada"
    )
