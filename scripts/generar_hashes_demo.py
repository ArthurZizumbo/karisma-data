"""Generate and verify the argon2id digests of the seeded portal users.

The tool prints; it never writes a file. That is deliberate. A generator that
rewrites the migration invites regenerating it, and an applied migration is
never edited (``db/AGENTS.md``). The digests are pasted once, by hand, into
``db/migrations/<timestamp>_create_app_user.sql``.

The shared demo password is read from ``KARISMA_DEMO_PASSWORD`` and never
appears in this file, in the SQL, in a test or in a document. Argon2 salts at
random, so two runs produce different digests for the same password and no test
can pin their value: what can be pinned, and is, is their format and their
correspondence, which is exactly what ``--verificar`` recomputes.

Usage::

    KARISMA_DEMO_PASSWORD=... poetry -P backend run python \
        scripts/generar_hashes_demo.py --sql
    KARISMA_DEMO_PASSWORD=... poetry -P backend run python \
        scripts/generar_hashes_demo.py --verificar
"""

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from app.core.scopes import Scope
from app.core.security import hash_password, verify_password

REPO_ROOT: Final[Path] = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR: Final[Path] = REPO_ROOT / "db" / "migrations"
MIGRATION_GLOB: Final[str] = "*_create_app_user.sql"

PASSWORD_VARIABLE: Final[str] = "KARISMA_DEMO_PASSWORD"  # noqa: S105
EMAIL_DOMAIN: Final[str] = "karisma.demo"

EXIT_OK: Final[int] = 0
EXIT_FAILED: Final[int] = 1
EXIT_MISUSE: Final[int] = 2

# One row of the INSERT, as the migration writes it. The digest is the only
# field the generator produces; the other four are the identity contract of
# section 4.0 of the US-015 plan.
SEED_ROW_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\(\s*'(?P<username>[a-z]+)'\s*,"
    r"\s*'(?P<email>[^']+)'\s*,"
    r"\s*'(?P<full_name>[^']+)'\s*,"
    r"\s*'(?P<hashed_password>\$argon2id\$[^']+)'\s*,"
    r"\s*'(?P<role>[a-z]+)'\s*\)"
)


@dataclass(frozen=True)
class SeedUser:
    """One of the seven users the migration seeds.

    Attributes:
        username: Login identifier and ``sub`` claim of the token.
        full_name: Name shown by the interface after signing in.
        role: Role of the user, from the canonical vocabulary.
    """

    username: str
    full_name: str
    role: Scope

    @property
    def email(self) -> str:
        """Return the contact address, always in the non resolvable demo domain.

        Returns:
            The address stored in ``app_user.email``.
        """
        return f"{self.username}@{EMAIL_DOMAIN}"


# The seven users of section 4.0 C-3 of the US-015 plan, in the order the
# migration writes them: the administrator first, then two per profile.
SEED_USERS: Final[tuple[SeedUser, ...]] = (
    SeedUser("movalle", "Mariana Ovalle", Scope.ADMIN),
    SeedUser("lmendez", "Laura Mendez", Scope.OPERATIVO),
    SeedUser("eruiz", "Elena Ruiz", Scope.OPERATIVO),
    SeedUser("dhernandez", "Diego Hernandez", Scope.ANALISTA),
    SeedUser("jmendieta", "Jorge Mendieta", Scope.ANALISTA),
    SeedUser("acastaneda", "Arturo Castaneda", Scope.DIRECTIVO),
    SeedUser("rvaldez", "Roberto Valdez", Scope.DIRECTIVO),
)


def read_password() -> str:
    """Return the demo password from the environment.

    Returns:
        The value of ``KARISMA_DEMO_PASSWORD``.

    Raises:
        SystemExit: If the variable is missing or empty. The tool never invents
            a default: a default would end up in the migration.
    """
    password = os.environ.get(PASSWORD_VARIABLE, "").strip()
    if not password:
        print(
            f"Falta {PASSWORD_VARIABLE} en el entorno. Su valor vive en "
            "backend/.env.local y en ningun archivo versionado.",
            file=sys.stderr,
        )
        raise SystemExit(EXIT_MISUSE)
    return password


def find_migration() -> Path:
    """Return the path of the ``create_app_user`` migration.

    Returns:
        The single matching file under ``db/migrations``.

    Raises:
        SystemExit: If no migration matches, or if more than one does.
    """
    matches = sorted(MIGRATIONS_DIR.glob(MIGRATION_GLOB))
    if len(matches) != 1:
        print(
            f"Se esperaba exactamente una migracion {MIGRATION_GLOB} en "
            f"{MIGRATIONS_DIR}, se encontraron {len(matches)}.",
            file=sys.stderr,
        )
        raise SystemExit(EXIT_MISUSE)
    return matches[0]


def render_sql(password: str) -> str:
    """Render the ``INSERT`` of the seven users with fresh digests.

    Args:
        password: Shared demo password, hashed once per user so that every row
            carries its own salt.

    Returns:
        The SQL statement, ready to be pasted into the migration.
    """
    # Two quotes, one comma and one separating space beyond the longest value,
    # so that even the widest row keeps its columns apart.
    padding = len("'',") + 1
    username_width = max(len(user.username) for user in SEED_USERS) + padding
    email_width = max(len(user.email) for user in SEED_USERS) + padding
    name_width = max(len(user.full_name) for user in SEED_USERS) + padding

    rows = []
    for user in SEED_USERS:
        username = f"'{user.username}',".ljust(username_width)
        email = f"'{user.email}',".ljust(email_width)
        full_name = f"'{user.full_name}',".ljust(name_width)
        digest = hash_password(password)
        rows.append(f"    ({username}{email}{full_name}'{digest}', '{user.role}')")

    columns = "username, email, full_name, hashed_password, role"
    header = f"INSERT INTO app_user ({columns}) VALUES"
    return header + "\n" + ",\n".join(rows) + ";"


def parse_seeded_rows(sql: str) -> list[re.Match[str]]:
    """Return one match per seeded row found in the migration.

    Args:
        sql: Full content of the migration file.

    Returns:
        The matches, in file order.
    """
    return list(SEED_ROW_PATTERN.finditer(sql))


def verify(password: str) -> int:
    """Recompute ``verify`` over every digest stored in the migration.

    Args:
        password: Shared demo password the digests must correspond to.

    Returns:
        ``0`` when the seven rows are present and every digest matches the
        password, ``1`` otherwise.
    """
    migration = find_migration()
    rows = parse_seeded_rows(migration.read_text(encoding="utf-8"))

    print(f"Migracion: {migration.relative_to(REPO_ROOT).as_posix()}")
    print(f"Filas sembradas encontradas: {len(rows)}")

    expected = {user.username: user for user in SEED_USERS}
    found = {match["username"] for match in rows}
    missing = sorted(set(expected) - found)
    unexpected = sorted(found - set(expected))
    failures: list[str] = []

    if missing:
        failures.append(f"faltan usuarios en la migracion: {missing}")
    if unexpected:
        failures.append(f"usuarios que el contrato no declara: {unexpected}")

    for match in rows:
        username = match["username"]
        matches_password = verify_password(password, match["hashed_password"])
        estado = "OK" if matches_password else "NO CORRESPONDE"
        print(f"  {username:<12} {match['role']:<10} {estado}")
        if not matches_password:
            failures.append(f"el hash de {username} no corresponde a la contrasena")
        user = expected.get(username)
        if user is not None and match["role"] != user.role:
            failures.append(
                f"el rol de {username} es {match['role']} y el contrato "
                f"dice {user.role}"
            )

    if failures:
        print("", file=sys.stderr)
        for failure in failures:
            print(f"FALLO: {failure}", file=sys.stderr)
        return EXIT_FAILED

    print(f"\nLos {len(rows)} hashes corresponden a {PASSWORD_VARIABLE}.")
    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    """Build the command line parser.

    Returns:
        The parser, with the two mutually exclusive and required modes.
    """
    parser = argparse.ArgumentParser(
        prog="generar_hashes_demo.py",
        description=(
            "Imprime el INSERT de los siete usuarios sembrados con hashes "
            "argon2id, o comprueba que los ya escritos corresponden a "
            f"{PASSWORD_VARIABLE}. Nunca escribe archivos."
        ),
    )
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument(
        "--sql",
        action="store_true",
        help="imprime el INSERT con hashes nuevos por salida estandar",
    )
    modes.add_argument(
        "--verificar",
        action="store_true",
        help="recomputa verify() sobre los hashes de la migracion",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the tool.

    Args:
        argv: Command line arguments, defaulting to ``sys.argv[1:]``.

    Returns:
        The process exit code.
    """
    arguments = build_parser().parse_args(argv)
    password = read_password()

    if arguments.sql:
        print(render_sql(password))
        return EXIT_OK
    return verify(password)


if __name__ == "__main__":
    raise SystemExit(main())
