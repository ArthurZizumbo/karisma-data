"""Tests for ``get_current_user``: the five ways of failing and the hierarchy.

``/api/auth/me`` is the endpoint of this US that declares no scope, so it is
where the 401 vectors are exercised. The hierarchy needs endpoints that do
declare one, and US-015 ships none: the probe application below mounts one route
per level, which is the harness for the rule US-016 inherits. If this file goes
red, the whole permission matrix of that US is built on sand.
"""

from collections.abc import Callable, Iterator
from typing import Annotated

import pytest
from conftest import MINIMAL_ENV, FakeUserRepository
from fastapi import FastAPI, Security
from fastapi.testclient import TestClient

# Imported at module level, and not inside each test as the rest of the suite
# does, because the probe application below declares its dependencies in
# annotations: FastAPI resolves those against the globals of the module, so a
# name bound inside a function would never be found.
from app.core.auth import get_current_user
from app.core.scopes import Scope
from app.models.user import AppUser, UserOut
from app.services.user_service import get_user_repository

RUTA_ME = "/api/auth/me"
USUARIO = "lmendez"

# Login identifier of a user seeded with each role, used to mint the tokens of
# the hierarchy matrix.
USUARIO_POR_ROL = {
    "operativo": "lmendez",
    "analista": "dhernandez",
    "directivo": "acastaneda",
    "admin": "movalle",
}

ORDEN_DE_ROLES = ("operativo", "analista", "directivo", "admin")

# Spelling of the fourth role in frontend/app/types/navegacion.ts, recorded as
# debt 2 of the handoff. It is the name a token would realistically carry by
# mistake, which is why the unknown scope of the case below is that one and not
# an invented string.
ROL_FUERA_DEL_VOCABULARIO = "administrador"


@pytest.fixture
def cliente_de_sonda(
    minimal_env: None, repositorio_falso: FakeUserRepository
) -> Iterator[TestClient]:
    """Return a client of an application with one route per scope level.

    Args:
        minimal_env: Declared so the environment is in place first.
        repositorio_falso: Double injected in place of the SQL repository.

    Yields:
        A started client of the probe application.
    """
    aplicacion = FastAPI()

    def construir(scope: str) -> Callable[..., object]:
        async def punto_final(
            usuario: Annotated[UserOut, Security(get_current_user, scopes=[scope])],
        ) -> dict[str, str]:
            return {"usuario": usuario.username}

        return punto_final

    for scope in Scope:
        aplicacion.add_api_route(
            f"/api/sonda/{scope.value}", construir(scope.value), methods=["GET"]
        )

    aplicacion.dependency_overrides[get_user_repository] = lambda: repositorio_falso
    with TestClient(aplicacion) as cliente:
        yield cliente


def test_sin_token_devuelve_401_con_cabecera(cliente: TestClient) -> None:
    """A request without credentials gets the typed 401 and its challenge.

    Args:
        cliente: Client bound to the repository double.
    """
    respuesta = cliente.get(RUTA_ME)

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "credenciales_ausentes"
    assert respuesta.headers["www-authenticate"] == 'Bearer realm="karisma"'


def test_token_firmado_con_otra_clave_es_401(
    cliente: TestClient, token_de: Callable[..., str]
) -> None:
    """A signature made with another key is rejected as an invalid token.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of forged tokens.
    """
    token = token_de(USUARIO, clave="otra-clave-de-firma-con-32-caracteres")

    respuesta = cliente.get(RUTA_ME, headers={"Authorization": f"Bearer {token}"})

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "credenciales_invalidas"
    assert 'error="invalid_token"' in respuesta.headers["www-authenticate"]


def test_token_vencido_es_401(
    cliente: TestClient, token_de: Callable[..., str]
) -> None:
    """An expired token is rejected, which is what makes the re-login clean.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of forged tokens.
    """
    token = token_de(USUARIO, vida_segundos=-1)

    respuesta = cliente.get(RUTA_ME, headers={"Authorization": f"Bearer {token}"})

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "sesion_expirada"
    assert (
        'error_description="sesion_expirada"' in respuesta.headers["www-authenticate"]
    )


def test_token_sin_scope_es_401(
    cliente: TestClient, token_de: Callable[..., str]
) -> None:
    """A token without the ``scope`` claim is rejected, not read as no permissions.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of forged tokens.
    """
    token = token_de(USUARIO, con_scope=False)

    respuesta = cliente.get(RUTA_ME, headers={"Authorization": f"Bearer {token}"})

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "credenciales_invalidas"


def test_usuario_deshabilitado_es_401(
    cliente: TestClient,
    token_de: Callable[..., str],
    usuarios_semilla: dict[str, AppUser],
) -> None:
    """The soft delete takes effect on the very next request.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of forged tokens.
        usuarios_semilla: Rows served by the double.
    """
    usuarios_semilla[USUARIO].disabled = True
    token = token_de(USUARIO)

    respuesta = cliente.get(RUTA_ME, headers={"Authorization": f"Bearer {token}"})

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "sesion_revocada"


def test_usuario_ausente_de_la_base_es_401(
    cliente: TestClient,
    token_de: Callable[..., str],
    usuarios_semilla: dict[str, AppUser],
) -> None:
    """A signed token over a row that no longer exists is not a session.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of forged tokens.
        usuarios_semilla: Rows served by the double, emptied of the caller.
    """
    token = token_de(USUARIO)
    del usuarios_semilla[USUARIO]

    respuesta = cliente.get(RUTA_ME, headers={"Authorization": f"Bearer {token}"})

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == "credenciales_invalidas"


def test_me_devuelve_la_identidad_sin_el_hash(
    cliente: TestClient, token_de: Callable[..., str]
) -> None:
    """The identity endpoint answers the contract and never the digest.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of forged tokens.
    """
    token = token_de(USUARIO)

    cuerpo = cliente.get(RUTA_ME, headers={"Authorization": f"Bearer {token}"}).json()

    assert set(cuerpo) == {
        "id",
        "username",
        "email",
        "full_name",
        "role",
        "disabled",
        "created_at",
    }
    assert cuerpo["username"] == USUARIO
    assert cuerpo["role"] == "operativo"


@pytest.mark.parametrize("rol_del_token", ORDEN_DE_ROLES)
@pytest.mark.parametrize("scope_exigido", ORDEN_DE_ROLES)
def test_jerarquia_de_roles(
    cliente_de_sonda: TestClient,
    token_de: Callable[..., str],
    rol_del_token: str,
    scope_exigido: str,
) -> None:
    """A role reaches every level at or below its own, and no other.

    Args:
        cliente_de_sonda: Client of the probe application.
        token_de: Factory of forged tokens.
        rol_del_token: Role carried by the token of the caller.
        scope_exigido: Scope declared by the endpoint under test.
    """
    token = token_de(USUARIO_POR_ROL[rol_del_token], rol_del_token)
    alcanza = ORDEN_DE_ROLES.index(rol_del_token) >= ORDEN_DE_ROLES.index(scope_exigido)

    respuesta = cliente_de_sonda.get(
        f"/api/sonda/{scope_exigido}", headers={"Authorization": f"Bearer {token}"}
    )

    assert respuesta.status_code == (200 if alcanza else 403)


def test_el_403_declara_insufficient_scope(
    cliente_de_sonda: TestClient, token_de: Callable[..., str]
) -> None:
    """The denial names the level demanded and nothing about the resource.

    Args:
        cliente_de_sonda: Client of the probe application.
        token_de: Factory of forged tokens.
    """
    token = token_de(USUARIO_POR_ROL["operativo"], "operativo")

    respuesta = cliente_de_sonda.get(
        "/api/sonda/admin", headers={"Authorization": f"Bearer {token}"}
    )

    assert respuesta.status_code == 403
    assert respuesta.json() == {"detail": "permisos_insuficientes"}
    assert respuesta.headers["www-authenticate"] == (
        'Bearer realm="karisma", error="insufficient_scope", scope="admin"'
    )


def test_un_scope_fuera_del_vocabulario_es_una_sesion_sin_permisos(
    cliente: TestClient,
    cliente_de_sonda: TestClient,
    token_de: Callable[..., str],
) -> None:
    """A role the portal cannot read grants nothing, and crashes nothing.

    ``parse_scope_claim`` drops names outside the vocabulary on purpose, so the
    safety of that decision rests entirely on the comparison failing closed
    when the set it produced is empty. Take that guard out and the next line
    asks for the ``max`` of an empty sequence: every scoped endpoint answers
    500 instead of denying. Invert it and a token carrying nothing this portal
    understands reaches all of them. The matrix above cannot see either defect:
    its sixteen cases all carry one of the four names.

    The two halves are one property. The endpoint that declares no scope still
    answers 200, because an unreadable permission is a session that grants
    nothing, not a session that does not exist -which is what a fix that raised
    on the unknown name would turn it into.

    Args:
        cliente_de_sonda: Client of the probe application.
        cliente: Client bound to the repository double.
        token_de: Factory of forged tokens.
    """
    token = token_de(USUARIO, ROL_FUERA_DEL_VOCABULARIO)
    cabeceras = {"Authorization": f"Bearer {token}"}

    sin_scope_exigido = cliente.get(RUTA_ME, headers=cabeceras)
    con_scope_exigido = cliente_de_sonda.get("/api/sonda/operativo", headers=cabeceras)

    assert sin_scope_exigido.status_code == 200
    assert con_scope_exigido.status_code == 403
    assert con_scope_exigido.json() == {"detail": "permisos_insuficientes"}


def test_el_401_de_un_endpoint_con_scope_publica_el_nivel(
    cliente_de_sonda: TestClient,
) -> None:
    """The 401 of a scoped endpoint echoes the scope a client should ask for.

    Args:
        cliente_de_sonda: Client of the probe application.
    """
    respuesta = cliente_de_sonda.get("/api/sonda/analista")

    assert respuesta.status_code == 401
    assert respuesta.headers["www-authenticate"] == (
        'Bearer realm="karisma", scope="analista"'
    )


def test_la_clave_de_firma_es_la_de_la_configuracion(
    cliente: TestClient, token_de: Callable[..., str]
) -> None:
    """A token signed with the configured key opens the session.

    The case guards the pair with ``test_token_firmado_con_otra_clave_es_401``:
    without it, a dependency that rejected everything would pass that one.

    Args:
        cliente: Client bound to the repository double.
        token_de: Factory of forged tokens.
    """
    token = token_de(USUARIO, clave=MINIMAL_ENV["JWT_SECRET_KEY"])

    respuesta = cliente.get(RUTA_ME, headers={"Authorization": f"Bearer {token}"})

    assert respuesta.status_code == 200
