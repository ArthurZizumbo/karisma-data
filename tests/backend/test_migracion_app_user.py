"""Contract tests over the versioned SQL of the ``create_app_user`` migration.

No test here opens a PostgreSQL connection: the subject is the text file that
git carries, which is the only artifact a deployment will replay. Argon2 salts
at random, so the digests cannot be pinned by value; what is pinned is their
format -``$argon2id$``- and their correspondence to the documented password,
which the ``--verificar`` mode of the generator recomputes outside the suite.

The identity of the seven users is read from ``scripts/generar_hashes_demo.py``,
the single Python declaration of the seed, so that a row edited by hand in the
SQL is caught instead of being blessed by a copy of itself.
"""

from __future__ import annotations

import re
from pathlib import Path

from generar_hashes_demo import SEED_ROW_PATTERN, SEED_USERS

from app.core.scopes import Scope

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "db" / "migrations"
SCHEMA_FILE = REPO_ROOT / "db" / "schema.sql"

MIGRACIONES = sorted(MIGRATIONS_DIR.glob("*_create_app_user.sql"))

# Assignments that would mean somebody wrote the password next to the digests,
# in a comment or in a column. The digest itself never matches: it is a value,
# never the right hand side of "password = ...".
CONTRASENA_EN_CLARO = re.compile(
    r"(contrasena|password|clave|passwd)\s*(=|:|es)\s*\S",
    re.IGNORECASE,
)

CHECK_DE_ROLES = re.compile(
    r"CHECK\s*\(\s*role\s+IN\s*\(([^)]*)\)\s*\)",
    re.IGNORECASE,
)


def test_la_migracion_existe() -> None:
    """Exactly one migration seeds the users.

    The guard exists so that no assertion below can pass over an empty file
    list, and so that a second copy of the seed is caught the day it appears.
    """
    assert len(MIGRACIONES) == 1, (
        f"Se esperaba una sola migracion create_app_user, hay {len(MIGRACIONES)}"
    )


def leer_sql() -> str:
    """Return the content of the seeding migration.

    Returns:
        The file decoded as UTF-8.
    """
    return MIGRACIONES[0].read_text(encoding="utf-8")


def filas_sembradas() -> list[re.Match[str]]:
    """Return one match per seeded row.

    Returns:
        The matches, in file order.
    """
    return list(SEED_ROW_PATTERN.finditer(leer_sql()))


def test_siembra_siete_usuarios() -> None:
    """The seed has seven rows and they are the ones the contract declares."""
    filas = filas_sembradas()

    assert len(filas) == len(SEED_USERS) == 7
    assert [fila["username"] for fila in filas] == [
        usuario.username for usuario in SEED_USERS
    ]


def test_cada_fila_lleva_el_correo_y_el_nombre_del_contrato() -> None:
    """Address and display name match the identity contract, user by user."""
    filas = {fila["username"]: fila for fila in filas_sembradas()}

    for usuario in SEED_USERS:
        fila = filas[usuario.username]
        assert fila["email"] == usuario.email
        assert fila["full_name"] == usuario.full_name
        assert fila["role"] == usuario.role.value


def test_todos_los_hashes_son_argon2id() -> None:
    """Every seeded digest is an argon2id one, and none is empty.

    This is the central assertion of the US: a plain password, an inherited
    bcrypt digest or an empty column all fail here.
    """
    filas = filas_sembradas()

    assert filas, "el INSERT no tiene filas reconocibles"
    for fila in filas:
        digest = fila["hashed_password"]
        assert digest.startswith("$argon2id$")
        assert len(digest) > len("$argon2id$v=19$m=65536,t=3,p=4$")


def test_no_hay_ninguna_contrasena_en_claro() -> None:
    """No line assigns a password, in a comment or anywhere else.

    The documented command names the variable, which is why the pattern demands
    an assignment: ``KARISMA_DEMO_PASSWORD=...`` in the header is prose about
    where the value lives, not the value.
    """
    sospechosas = [
        linea
        for linea in leer_sql().splitlines()
        if CONTRASENA_EN_CLARO.search(linea)
        and "KARISMA_DEMO_PASSWORD=..." not in linea
        and "hashed_password" not in linea
    ]

    assert not sospechosas, f"lineas que parecen escribir una contrasena: {sospechosas}"


def test_un_admin_y_dos_por_perfil() -> None:
    """The seed keeps the composition ``db/AGENTS.md`` describes."""
    roles = [fila["role"] for fila in filas_sembradas()]

    assert roles.count("admin") == 1
    for rol in (Scope.OPERATIVO, Scope.ANALISTA, Scope.DIRECTIVO):
        assert roles.count(rol.value) == 2


def test_usuarios_y_correos_son_unicos() -> None:
    """No identifier and no address repeats, which is what the UNIQUE backs."""
    filas = filas_sembradas()
    usuarios = [fila["username"] for fila in filas]
    correos = [fila["email"] for fila in filas]

    assert len(set(usuarios)) == len(usuarios)
    assert len(set(correos)) == len(correos)


def test_los_valores_de_Scope_coinciden_con_el_CHECK() -> None:  # noqa: N802
    """The Python vocabulary and the database constraint say the same four names.

    It is the only test that ties the two artifacts: a role added in Python
    without a migration -or the reverse- ends here.
    """
    encontrado = CHECK_DE_ROLES.search(leer_sql())

    assert encontrado is not None, "la tabla no declara CHECK sobre role"
    del_check = {valor.strip().strip("'") for valor in encontrado.group(1).split(",")}
    assert del_check == {scope.value for scope in Scope}


def test_la_tabla_declara_las_columnas_del_modelo() -> None:
    """The columns the SQLModel mirror declares exist in the migration.

    The model never creates schema, so nothing but this assertion notices when
    the two drift apart.
    """
    from app.models.user import AppUser

    sql = leer_sql().lower()

    for columna in AppUser.model_fields:
        assert f"{columna} " in sql, f"la migracion no crea la columna {columna}"


def test_la_bajada_elimina_la_tabla() -> None:
    """The rollback drops the table: a migration without reverse is not one."""
    sql = leer_sql()
    bajada = sql.split("-- migrate:down", 1)[1]

    assert "DROP TABLE IF EXISTS app_user;" in bajada


def test_la_baja_logica_esta_en_el_esquema() -> None:
    """``disabled`` exists with its default, which is what makes the soft delete."""
    sql = leer_sql()

    assert re.search(
        r"disabled\s+BOOLEAN\s+NOT NULL\s+DEFAULT\s+false", sql, re.IGNORECASE
    )
    assert "DELETE FROM app_user" not in sql.upper()


def test_el_volcado_versionado_refleja_la_tabla() -> None:
    """``db/schema.sql`` carries the table, so ``make db-up`` really ran."""
    schema = SCHEMA_FILE.read_text(encoding="utf-8")

    assert "CREATE TABLE public.app_user" in schema
    assert "app_user_username_key UNIQUE (username)" in schema
    assert "app_user_email_key UNIQUE (email)" in schema


def test_el_volcado_no_contiene_ningun_hash() -> None:
    """The dump is schema only: the seeded rows never travel into it.

    A ``pg_dump`` that started including data would put seven digests in a file
    that is diffed byte by byte in CI, and nobody would notice for weeks.
    """
    assert "$argon2id$" not in SCHEMA_FILE.read_text(encoding="utf-8")


# Deliberately absent: a parametrized check that each contract user appears in
# the SQL. Its assertion -the username shows up somewhere in the file- is
# strictly contained in test_siembra_siete_usuarios, which pins the whole list
# in order, and in the one above, which pins address, name and role row by row.
# It could not fail without one of those two failing first, so it would buy
# seven green marks and no information.
