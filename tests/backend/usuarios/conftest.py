"""Fixtures of the user administration suite: the double, the client and tokens.

The fixtures of ``tests/backend/conftest.py`` are inherited untouched -the
minimal environment, the seven seeded doubles, the read repository double and
the token factory- and only what this suite adds lives here. That file belongs
to US-015 and this suite never opens it: widening its ``FakeUserRepository``
would have been the cheap move and it would have broken four other modules.

Nothing here opens PostgreSQL. The application is the real one, mounted by
``create_app``, and only two seams are substituted: ``get_user_repository``, so
``get_current_user`` resolves the caller from the seeded doubles, and
``get_admin_user_repository``, so the administration side answers from memory.
The authorization dependency, the scopes and the routers are production code in
every test of this package, which is what makes the 401 and the 403 real.
"""

import uuid
from collections.abc import Callable, Iterator, Sequence
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Final, cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.dialects.postgresql.base import PGDialect
from sqlalchemy.engine import Dialect
from sqlalchemy.sql import ClauseElement

from app.core.scopes import Scope
from app.models.user import UserAdminOut
from app.services.user_service import get_admin_user_repository, get_user_repository

if TYPE_CHECKING:
    from conftest import FakeUserRepository

    from app.models.user import AppUser

# Login identifier of the administrator the suite signs in as. It is one of the
# seven users the migration of US-015 seeds, never an invented name.
ADMIN: Final[str] = "movalle"

# Somebody else to act upon, so the self protection rule is not the only path
# the suite exercises.
OTRO: Final[str] = "dhernandez"

# Instant the double stamps on the first write. Later than the seeded
# ``created_at`` so "the modification is after the creation" is an assertion
# with content and not an accident of the clock.
PRIMERA_ESCRITURA: Final[datetime] = datetime(2026, 8, 13, 9, 0, tzinfo=UTC)

# Description of PostgreSQL used to render the statements the repository builds.
# It is not a connection and nothing here opens one; SQLAlchemy leaves the
# constructor of its dialects unannotated, hence the narrow ignore.
_DIALECTO: Final[Dialect] = PGDialect()  # type: ignore[no-untyped-call]


class FakeAdminUserRepository:
    """In-memory double of ``AdminUserRepository``.

    It records the name of every method it is asked for, which is what lets a
    test show that the self protection rule is decided *before* the database is
    touched instead of after the row has already been written.

    Attributes:
        filas: Rows indexed by primary key.
        llamadas: Names of the repository methods invoked, in order.
    """

    def __init__(self, filas: dict[uuid.UUID, UserAdminOut]) -> None:
        """Store the rows this repository will serve.

        Args:
            filas: Rows indexed by primary key.
        """
        self.filas = filas
        self.llamadas: list[str] = []
        self._escrituras = 0

    async def list_page(
        self, *, limit: int, offset: int
    ) -> tuple[Sequence[UserAdminOut], int]:
        """Return one page and the size of the whole collection.

        Args:
            limit: Page size.
            offset: Rows skipped before the page.

        Returns:
            The page, in the order the protocol promises, and the total.
        """
        self.llamadas.append("list_page")
        ordenadas = sorted(self.filas.values(), key=lambda fila: fila.username)
        return ordenadas[offset : offset + limit], len(ordenadas)

    async def get_by_id(self, user_id: uuid.UUID) -> UserAdminOut | None:
        """Return one row by primary key.

        Args:
            user_id: Primary key of the row.

        Returns:
            The row, or ``None`` when nobody carries that identifier.
        """
        self.llamadas.append("get_by_id")
        return self.filas.get(user_id)

    async def update_role(self, user_id: uuid.UUID, role: Scope) -> UserAdminOut | None:
        """Write the role and stamp the modification.

        Args:
            user_id: Primary key of the row.
            role: Role to store.

        Returns:
            The updated row, or ``None`` when nobody carries that identifier.
        """
        self.llamadas.append("update_role")
        return self._escribir(user_id, {"role": role})

    async def set_disabled(
        self, user_id: uuid.UUID, disabled: bool
    ) -> UserAdminOut | None:
        """Write the soft delete flag and stamp the modification.

        Args:
            user_id: Primary key of the row.
            disabled: New value of the flag.

        Returns:
            The updated row, or ``None`` when nobody carries that identifier.
        """
        self.llamadas.append("set_disabled")
        return self._escribir(user_id, {"disabled": disabled})

    def _escribir(
        self, user_id: uuid.UUID, cambios: dict[str, object]
    ) -> UserAdminOut | None:
        """Apply the change and move the modification stamp forward.

        Args:
            user_id: Primary key of the row.
            cambios: Fields to overwrite.

        Returns:
            The updated row, or ``None`` when nobody carries that identifier.
        """
        fila = self.filas.get(user_id)
        if fila is None:
            return None
        self._escrituras += 1
        marca = PRIMERA_ESCRITURA + timedelta(seconds=self._escrituras)
        actualizada = fila.model_copy(update={**cambios, "updated_at": marca})
        self.filas[user_id] = actualizada
        return actualizada


@pytest.fixture
def filas_admin(
    usuarios_semilla: "dict[str, AppUser]",
) -> dict[uuid.UUID, UserAdminOut]:
    """Return the seven seeded users as administration rows, indexed by key.

    ``updated_at`` starts equal to ``created_at``, which is exactly what the
    migration does to the seeded rows: an account nobody has touched must not
    read as modified the day the column was added.

    Args:
        usuarios_semilla: Doubles of the seven users the migration seeds.

    Returns:
        The rows the administration double will serve.
    """
    filas: dict[uuid.UUID, UserAdminOut] = {}
    for usuario in usuarios_semilla.values():
        assert usuario.id is not None
        assert usuario.created_at is not None
        filas[usuario.id] = UserAdminOut(
            id=usuario.id,
            username=usuario.username,
            email=usuario.email,
            full_name=usuario.full_name,
            role=Scope(usuario.role),
            disabled=usuario.disabled,
            created_at=usuario.created_at,
            updated_at=usuario.created_at,
        )
    return filas


@pytest.fixture
def repositorio_admin_falso(
    filas_admin: dict[uuid.UUID, UserAdminOut],
) -> FakeAdminUserRepository:
    """Return the administration double serving the seeded rows.

    Args:
        filas_admin: Rows the double will serve.

    Returns:
        The double, ready to be injected through ``dependency_overrides``.
    """
    return FakeAdminUserRepository(filas_admin)


@pytest.fixture
def cliente_admin(
    minimal_env: None,
    repositorio_falso: "FakeUserRepository",
    repositorio_admin_falso: FakeAdminUserRepository,
) -> Iterator[TestClient]:
    """Return a client of the real application with both repositories doubled.

    Args:
        minimal_env: Declared so the environment is in place before the
            settings are read.
        repositorio_falso: Read side, consumed by ``get_current_user``.
        repositorio_admin_falso: Administration side, consumed by the router.

    Yields:
        A started client of the real application.
    """
    from app.main import create_app

    aplicacion = create_app()
    aplicacion.dependency_overrides[get_user_repository] = lambda: repositorio_falso
    aplicacion.dependency_overrides[get_admin_user_repository] = lambda: (
        repositorio_admin_falso
    )
    with TestClient(aplicacion) as cliente:
        yield cliente


@pytest.fixture
def usuario_por_rol(usuarios_semilla: "dict[str, AppUser]") -> dict[Scope, str]:
    """Map each role to the login identifier of one seeded user carrying it.

    Derived from the seed and not retyped, so a change to the seeded users moves
    the parametrized matrix with it instead of leaving a stale literal behind.

    Args:
        usuarios_semilla: Doubles of the seven seeded users.

    Returns:
        One login identifier per role.
    """
    por_rol: dict[Scope, str] = {}
    for usuario in usuarios_semilla.values():
        por_rol.setdefault(Scope(usuario.role), usuario.username)
    faltantes = sorted(scope.value for scope in Scope if scope not in por_rol)
    assert not faltantes, f"la semilla no cubre los roles {faltantes}"
    return por_rol


@pytest.fixture
def cabecera_de(
    usuario_por_rol: dict[Scope, str], token_de: Callable[..., str]
) -> Callable[[Scope], dict[str, str]]:
    """Return a factory of ``Authorization`` headers for a role.

    Args:
        usuario_por_rol: Login identifier of a seeded user per role.
        token_de: Factory of signed tokens from the parent conftest.

    Returns:
        A callable taking a role and returning the header of that role.
    """

    def _cabecera(rol: Scope) -> dict[str, str]:
        return {"Authorization": f"Bearer {token_de(usuario_por_rol[rol], rol.value)}"}

    return _cabecera


@pytest.fixture
def cabecera_admin(
    cabecera_de: Callable[[Scope], dict[str, str]],
) -> dict[str, str]:
    """Return the ``Authorization`` header of the seeded administrator.

    Args:
        cabecera_de: Factory of headers per role.

    Returns:
        The header the administration tests send.
    """
    return cabecera_de(Scope.ADMIN)


@pytest.fixture
def id_de(usuarios_semilla: "dict[str, AppUser]") -> Callable[[str], uuid.UUID]:
    """Return a lookup from login identifier to primary key.

    Args:
        usuarios_semilla: Doubles of the seven seeded users.

    Returns:
        A callable taking a login identifier and returning its key.
    """

    def _id(username: str) -> uuid.UUID:
        usuario = usuarios_semilla[username]
        assert usuario.id is not None
        return usuario.id

    return _id


class _Resultado:
    """Result double: whatever rows the spy session was told to serve.

    Attributes:
        filas: Rows handed back, in the order the projection declares them.
    """

    def __init__(self, filas: tuple[tuple[object, ...], ...]) -> None:
        """Store the rows this result will serve.

        Args:
            filas: Rows as tuples, positional like a real projected row.
        """
        self.filas = filas

    def all(self) -> list[tuple[object, ...]]:
        """Return every row.

        Returns:
            The rows, as a list.
        """
        return list(self.filas)

    def first(self) -> tuple[object, ...] | None:
        """Return the first row.

        Returns:
            The first row, or ``None`` when there is none.
        """
        return self.filas[0] if self.filas else None


class SesionEspia:
    """Session double that records the statements instead of executing them.

    It is what lets the only layer of the project that writes SQL be inspected
    without PostgreSQL: the statements are real, built by production code, and
    the assertions compile them with the PostgreSQL dialect of SQLAlchemy. It
    does not replace the manual test against the real database -it cannot see a
    typo in a column name that the mapper also carries- but it does catch the
    two defects that would be invisible until production: a projection that
    reads the password digest and a listing without ORDER BY.

    Attributes:
        sentencias: Statements the repository handed over, in order.
        confirmaciones: Number of times the repository committed.
    """

    def __init__(self, filas: tuple[tuple[object, ...], ...] = ()) -> None:
        """Start with no recorded statement.

        Args:
            filas: Rows every statement will answer with. Empty by default,
                which is what the guards over the generated SQL need; a test
                about the mapping of a row passes one in.
        """
        self.sentencias: list[ClauseElement] = []
        self.confirmaciones = 0
        self._filas = filas

    async def execute(self, statement: ClauseElement) -> _Resultado:
        """Record the statement and answer with the configured rows.

        Args:
            statement: Statement built by the repository.

        Returns:
            A result carrying the rows the spy was built with.
        """
        self.sentencias.append(statement)
        return _Resultado(self._filas)

    async def scalar(self, statement: ClauseElement) -> int:
        """Record the statement and answer as a count of zero.

        Args:
            statement: Statement built by the repository.

        Returns:
            Zero.
        """
        self.sentencias.append(statement)
        return 0

    async def commit(self) -> None:
        """Record that the repository asked to commit."""
        self.confirmaciones += 1


def sql_de(statement: ClauseElement, *, literales: bool = False) -> str:
    """Compile a statement with the PostgreSQL dialect and return its text.

    Args:
        statement: Statement recorded by the spy session.
        literales: Whether to inline bound parameters, so a test can assert on
            the page window and not only on the presence of the keyword.

    Returns:
        The SQL as PostgreSQL would receive it.
    """
    opciones = {"literal_binds": True} if literales else {}
    # ClauseElement.compile carries a decorator SQLAlchemy leaves unannotated,
    # so mypy reads the call as untyped. Naming the bound method through a cast
    # keeps the type of this helper without silencing anything wider.
    compilar = cast(Callable[..., object], statement.compile)
    return str(compilar(dialect=_DIALECTO, compile_kwargs=opciones))


@pytest.fixture
def sesion_espia() -> SesionEspia:
    """Return a session double that records statements without a server.

    Returns:
        The spy, ready to be handed to ``SqlAdminUserRepository``.
    """
    return SesionEspia()
