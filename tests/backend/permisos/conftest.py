"""Fixtures of the permission suite: the probe application and its tokens.

The fixtures of ``tests/backend/conftest.py`` are inherited untouched -the
minimal environment, the seeded doubles, the repository double and the token
factory- and only what this suite adds lives here.

The probe application is the harness of the matrix. Its endpoints are not the
subject of the tests: they are probes, one per level of the policy, and what
they exercise is the production dependency of ``app.core.auth`` and the
hierarchy of ``app.core.scopes``. The user lookup enters through
``get_user_repository``, so the whole matrix runs without PostgreSQL.

``app.main`` is imported inside the fixtures and never at module level: that
module builds an application as its last statement, so importing it before the
environment fixture has run would read the settings of the developer machine.
"""

from collections.abc import Callable, Coroutine, Iterator, Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Annotated, Any, Final

import pytest
from conftest import FakeUserRepository
from fastapi import FastAPI, Security
from fastapi.testclient import TestClient

# Imported at module level, and not inside each fixture as the parent conftest
# does, because the probe endpoints below declare their dependencies in
# annotations: FastAPI resolves those against the globals of the module where
# the function was defined, so a name bound inside a fixture would never be
# found. None of these modules touches the settings at import time.
from app.core.auth import get_current_user
from app.core.scopes import Scope
from app.models.user import UserOut
from app.services.user_service import get_user_repository

if TYPE_CHECKING:
    from app.models.user import AppUser

# One probe per level of the policy, with the scopes each level declares.
SONDAS: Final[Mapping[str, tuple[Scope, ...]]] = MappingProxyType(
    {
        "catalogo": (),
        "consulta": (Scope.OPERATIVO,),
        "agregacion": (Scope.ANALISTA,),
        "resumen": (Scope.DIRECTIVO,),
        "usuarios": (Scope.ADMIN,),
    }
)

# Route of the probe application that carries no security at all. It is what
# shows that the 401 of an anonymous request comes from the dependency and not
# from something global to the application.
RUTA_PUBLICA: Final[str] = "/api/probe/publico"


def ruta_de(nivel: str) -> str:
    """Return the path of the probe of a level.

    Args:
        nivel: Key of ``SONDAS``.

    Returns:
        The path the probe application serves.
    """
    return f"/api/probe/{nivel}"


def _construir_sonda(
    scopes: list[str],
) -> Callable[..., Coroutine[Any, Any, dict[str, str]]]:
    """Build a probe endpoint that demands the given scopes.

    Args:
        scopes: Scope names declared through ``Security``.

    Returns:
        The endpoint function, ready to be mounted.
    """

    async def punto_final(
        usuario: Annotated[UserOut, Security(get_current_user, scopes=scopes)],
    ) -> dict[str, str]:
        """Answer with the identity the security dependency resolved.

        Args:
            usuario: Caller resolved by the security dependency.

        Returns:
            The login identifier of the caller.
        """
        return {"usuario": usuario.username}

    return punto_final


async def _punto_final_publico() -> dict[str, str]:
    """Answer without asking for credentials.

    Returns:
        A fixed payload.
    """
    return {"estado": "publico"}


@pytest.fixture
def aplicacion_de_sonda(minimal_env: None) -> FastAPI:
    """Return an application with one route per level of the policy.

    Args:
        minimal_env: Declared so the environment is in place before ``app`` is
            used.

    Returns:
        The probe application, without the repository override.
    """
    aplicacion = FastAPI()
    aplicacion.add_api_route(
        RUTA_PUBLICA, _punto_final_publico, methods=["GET"], name="publico"
    )
    for nivel, scopes in SONDAS.items():
        aplicacion.add_api_route(
            ruta_de(nivel),
            _construir_sonda([scope.value for scope in scopes]),
            methods=["GET"],
            name=nivel,
        )
    return aplicacion


@pytest.fixture
def cliente_de_sonda(
    aplicacion_de_sonda: FastAPI, repositorio_falso: FakeUserRepository
) -> Iterator[TestClient]:
    """Return a started client of the probe application.

    Args:
        aplicacion_de_sonda: Application with one route per level.
        repositorio_falso: Double injected in place of the SQL repository.

    Yields:
        A client bound to the repository double.
    """
    aplicacion_de_sonda.dependency_overrides[get_user_repository] = lambda: (
        repositorio_falso
    )
    with TestClient(aplicacion_de_sonda) as cliente:
        yield cliente


@pytest.fixture
def usuario_por_rol(usuarios_semilla: dict[str, "AppUser"]) -> dict[Scope, str]:
    """Map each role to the login identifier of one seeded user carrying it.

    The mapping is derived from the seed and not retyped, so a change to the
    seeded users moves the matrix with it instead of leaving a stale literal.

    Args:
        usuarios_semilla: Rows served by the repository double.

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
def token_de_rol(
    usuario_por_rol: dict[Scope, str], token_de: Callable[..., str]
) -> Callable[[Scope], str]:
    """Return a factory of valid tokens for a role.

    Args:
        usuario_por_rol: Login identifier of a seeded user per role.
        token_de: Factory of signed tokens from the parent conftest.

    Returns:
        A callable taking a role and returning its encoded token.
    """

    def _token(rol: Scope) -> str:
        return token_de(usuario_por_rol[rol], rol.value)

    return _token


@pytest.fixture
def crear_aplicacion(
    minimal_env: None, monkeypatch: pytest.MonkeyPatch
) -> Callable[..., FastAPI]:
    """Return a factory of real applications, with the demo flag on or off.

    The flag is applied before the factory runs because it decides whether a
    router is mounted at all, and the guard audits the application it is given,
    not the source code.

    Args:
        minimal_env: Declared so the environment is in place first.
        monkeypatch: Used to set the flag before the settings are read.

    Returns:
        A callable taking ``demo`` and returning a freshly built application.
    """
    from app.core.config import get_settings
    from app.main import create_app

    def _crear(*, demo: bool = False) -> FastAPI:
        monkeypatch.setenv("DEMO_LOGIN_ENABLED", "true" if demo else "false")
        get_settings.cache_clear()
        return create_app()

    return _crear
