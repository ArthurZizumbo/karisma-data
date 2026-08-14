"""Shared fixtures for the backend test suite.

The suite is invoked from the repository root while the application lives in
``backend/``. The path bootstrap below keeps ``pytest tests/backend`` working
even when pytest is started without ``-c backend/pyproject.toml``, which is the
only way it would pick up the ``pythonpath`` setting of that file. Everything
that imports ``app`` is therefore imported inside the fixtures, after the
bootstrap has run.

``scripts/`` joins the path for the same reason: ``generar_hashes_demo`` is the
tool that declares the seven seeded users, and both the fixtures below and the
migration contract test read that single declaration instead of retyping it.

No fixture here opens a PostgreSQL connection. Authentication runs against a
double of ``UserRepository``, which is what keeps the property US-002
established -no test needs a database- while still exercising the 401, the 403
and the disabled user.
"""

import sys
import time
import uuid
from collections.abc import Callable, Iterator
from contextlib import ExitStack
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from fastapi.testclient import TestClient

if TYPE_CHECKING:
    from app.models.user import AppUser

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
SCRIPTS_ROOT = REPO_ROOT / "scripts"
for _root in (BACKEND_ROOT, SCRIPTS_ROOT):
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

MINIMAL_ENV: dict[str, str] = {
    "DATABASE_URL": "postgresql://karisma:karisma@localhost:5432/karisma_test",
    # 43 characters: the settings now enforce a 32 character minimum, so a
    # short placeholder would fail validation instead of the case under test.
    "JWT_SECRET_KEY": "test-signing-key-with-enough-entropy-000000",
    "GEMINI_API_KEY": "test-gemini-key",
    "APP_ENV": "test",
    "LOG_LEVEL": "WARNING",
    # Pinned so that a developer who exported the flag in their shell does not
    # silently change which routers the application under test mounts.
    "DEMO_LOGIN_ENABLED": "false",
}

# Password shared by the doubles of the seeded users. It is a test value and has
# nothing to do with KARISMA_DEMO_PASSWORD, which lives only in backend/.env.local
# and never reaches a versioned file.
CONTRASENA_DE_PRUEBA = "contrasena-de-prueba-de-us-015"


@pytest.fixture(autouse=True)
def minimal_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    """Provide the minimum viable environment and isolate the settings cache.

    The working directory is moved to an empty temporary folder so that no
    ``.env.local`` of the developer machine leaks into the assertions, and the
    ``lru_cache`` of ``get_settings`` is cleared on both sides of the test.

    Args:
        monkeypatch: Fixture used to patch the environment and the cwd.
        tmp_path: Empty directory used as the working directory of the test.

    Yields:
        None. The fixture only manipulates process-wide state.
    """
    from app.core.config import get_settings

    monkeypatch.chdir(tmp_path)
    for name, value in MINIMAL_ENV.items():
        monkeypatch.setenv(name, value)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client(minimal_env: None) -> Iterator[TestClient]:
    """Return a test client bound to a freshly built application.

    Args:
        minimal_env: Declared explicitly to guarantee that the environment is
            in place before the application factory reads the settings.

    Yields:
        A client that runs the startup and shutdown handlers of the app.
    """
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


class FakeUserRepository:
    """In-memory double of ``UserRepository``.

    It records every identifier it is asked for, which is what lets a test show
    that the demo access looks up the canonical user instead of trusting the
    body of the request.
    """

    def __init__(self, usuarios: dict[str, "AppUser"]) -> None:
        """Store the rows this repository will serve.

        Args:
            usuarios: Rows indexed by login identifier.
        """
        self.usuarios = usuarios
        self.consultas: list[str] = []

    async def get_by_username(self, username: str) -> "AppUser | None":
        """Return the row with that login identifier.

        Args:
            username: Login identifier, as typed by the caller.

        Returns:
            The row, or ``None`` when nobody carries that identifier.
        """
        self.consultas.append(username)
        return self.usuarios.get(username)


@lru_cache(maxsize=1)
def digest_de_prueba() -> str:
    """Return the argon2id digest of the test password, computed once.

    Hashing is deliberately slow, and the seven doubles share one password, so
    computing the digest once per session keeps the suite fast without weakening
    anything: what the tests exercise is the verification, not the salt.

    Returns:
        The digest every seeded double carries.
    """
    from app.core.security import hash_password

    return hash_password(CONTRASENA_DE_PRUEBA)


@pytest.fixture
def usuarios_semilla(minimal_env: None) -> dict[str, "AppUser"]:
    """Return doubles of the seven users the migration seeds, indexed by name.

    The identity of each row -identifier, address, name and role- comes from the
    single declaration in ``scripts/generar_hashes_demo.py``, so a change to the
    seed contract moves the fixtures and the migration test together.

    Args:
        minimal_env: Declared so the environment is in place before ``app`` is
            imported.

    Returns:
        Freshly built rows, safe for a test to mutate.
    """
    from generar_hashes_demo import SEED_USERS

    from app.models.user import AppUser

    return {
        user.username: AppUser(
            id=uuid.uuid5(uuid.NAMESPACE_DNS, user.username),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=digest_de_prueba(),
            role=user.role.value,
            disabled=False,
            created_at=datetime(2026, 8, 11, 12, 0, tzinfo=UTC),
        )
        for user in SEED_USERS
    }


@pytest.fixture
def repositorio_falso(usuarios_semilla: dict[str, "AppUser"]) -> FakeUserRepository:
    """Return a repository double serving the seeded users.

    Args:
        usuarios_semilla: Rows the double will serve.

    Returns:
        The double, ready to be injected through ``dependency_overrides``.
    """
    return FakeUserRepository(usuarios_semilla)


@pytest.fixture
def crear_cliente(
    minimal_env: None,
    repositorio_falso: FakeUserRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Callable[..., TestClient]]:
    """Return a factory of clients bound to the repository double.

    The flag of the demo access is applied before the application is built,
    because it decides whether a router is mounted at all and not what an
    endpoint answers.

    Args:
        minimal_env: Declared so the environment is in place first.
        repositorio_falso: Double injected in place of the SQL repository.
        monkeypatch: Used to set the flag before the settings are read.

    Yields:
        A callable taking ``demo`` and returning a started client.
    """
    from app.core.config import get_settings
    from app.main import create_app
    from app.services.user_service import get_user_repository

    with ExitStack() as stack:

        def _crear(*, demo: bool = True) -> TestClient:
            monkeypatch.setenv("DEMO_LOGIN_ENABLED", "true" if demo else "false")
            get_settings.cache_clear()
            aplicacion = create_app()
            aplicacion.dependency_overrides[get_user_repository] = lambda: (
                repositorio_falso
            )
            return stack.enter_context(TestClient(aplicacion))

        yield _crear


@pytest.fixture
def cliente(crear_cliente: Callable[..., TestClient]) -> TestClient:
    """Return a client with the demo access mounted.

    Args:
        crear_cliente: Factory of clients bound to the repository double.

    Returns:
        A started client.
    """
    return crear_cliente(demo=True)


@pytest.fixture
def token_de(minimal_env: None) -> Callable[..., str]:
    """Return a factory of access tokens signed for the test environment.

    The factory writes the claims by hand instead of calling
    ``create_access_token`` so that a test can forge exactly the token it needs:
    signed with another key, already expired, or without the ``scope`` claim.

    Args:
        minimal_env: Declared so the signing key is in place.

    Returns:
        A callable that returns an encoded token.
    """
    import jwt

    from app.core.config import get_settings
    from app.core.scopes import Scope
    from app.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

    def _token(
        username: str,
        rol: str = Scope.OPERATIVO.value,
        *,
        vida_segundos: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        clave: str | None = None,
        con_scope: bool = True,
    ) -> str:
        emitido = int(time.time())
        claims: dict[str, str | int] = {"sub": username, "exp": emitido + vida_segundos}
        claims["iat"] = emitido
        if con_scope:
            claims["scope"] = rol
        return jwt.encode(
            claims,
            clave if clave is not None else get_settings().jwt_secret_key,
            algorithm=ALGORITHM,
        )

    return _token
