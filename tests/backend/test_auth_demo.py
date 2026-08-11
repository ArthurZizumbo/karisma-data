"""Tests for ``POST /api/auth/demo``, the credential-free access of the prototype.

Two properties carry the whole design. The route exists if and only if
``DEMO_LOGIN_ENABLED`` is on -it is a router that is not mounted, not an
endpoint with a condition inside- and the scopes of the token it mints come from
the row of the canonical user, never from the body of the request.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import jwt
import pytest
from conftest import MINIMAL_ENV

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi.testclient import TestClient

    from app.models.user import AppUser

RUTA_DEMO = "/api/auth/demo"
ROLES = ("operativo", "analista", "directivo", "admin")


def test_con_bandera_apagada_la_ruta_no_existe(
    crear_cliente: Callable[..., TestClient], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Off, the door is not there: 404 and nothing in the published schema.

    A 403 would confirm the endpoint exists. ``APP_ENV`` is moved to ``local``
    because the application only publishes ``/openapi.json`` there.

    Args:
        crear_cliente: Factory of clients bound to the repository double.
        monkeypatch: Used to expose the schema for this case.
    """
    monkeypatch.setenv("APP_ENV", "local")
    cliente = crear_cliente(demo=False)

    assert cliente.post(RUTA_DEMO, json={"rol": "admin"}).status_code == 404
    assert RUTA_DEMO not in cliente.get("/openapi.json").json()["paths"]


def test_con_bandera_encendida_la_ruta_se_publica(
    crear_cliente: Callable[..., TestClient], monkeypatch: pytest.MonkeyPatch
) -> None:
    """On, the route is mounted and announced, and the application still boots.

    Args:
        crear_cliente: Factory of clients bound to the repository double.
        monkeypatch: Used to expose the schema for this case.
    """
    monkeypatch.setenv("APP_ENV", "local")
    cliente = crear_cliente(demo=True)

    esquema = cliente.get("/openapi.json").json()

    assert RUTA_DEMO in esquema["paths"]
    assert "demostracion" in esquema["paths"][RUTA_DEMO]["post"]["summary"]


@pytest.mark.parametrize("rol", ROLES)
def test_cada_rol_entra_como_su_usuario_canonico(cliente: TestClient, rol: str) -> None:
    """Each role signs in as the user the map declares, with that role in the claim.

    Args:
        cliente: Client with the demo access mounted.
        rol: Role requested in the body.
    """
    from app.core.scopes import Scope
    from app.services.auth_service import DEMO_USERNAME_BY_ROLE

    respuesta = cliente.post(RUTA_DEMO, json={"rol": rol})

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["modo"] == "demostracion"
    assert cuerpo["token_type"] == "bearer"
    claims = jwt.decode(
        cuerpo["access_token"], MINIMAL_ENV["JWT_SECRET_KEY"], algorithms=["HS256"]
    )
    assert claims["sub"] == DEMO_USERNAME_BY_ROLE[Scope(rol)]
    assert claims["scope"] == rol


def test_los_usuarios_canonicos_estan_sembrados(
    usuarios_semilla: dict[str, AppUser],
) -> None:
    """The map points at users the migration actually seeds, with that role.

    Args:
        usuarios_semilla: Rows the migration contract declares.
    """
    from app.services.auth_service import DEMO_USERNAME_BY_ROLE

    for rol, username in DEMO_USERNAME_BY_ROLE.items():
        assert username in usuarios_semilla
        assert usuarios_semilla[username].role == rol


def test_rol_desconocido_es_422(cliente: TestClient) -> None:
    """An invented role is a validation error, never a token.

    Args:
        cliente: Client with the demo access mounted.
    """
    respuesta = cliente.post(RUTA_DEMO, json={"rol": "administrador"})

    assert respuesta.status_code == 422
    assert "access_token" not in respuesta.text


def test_el_scope_sale_de_la_fila_y_no_del_cuerpo(
    cliente: TestClient, usuarios_semilla: dict[str, AppUser]
) -> None:
    """The body selects the user; the row decides the scope.

    Demoting the canonical administrator must demote the demo token with it. If
    the claim were copied from the request, this door would be an escalation.

    Args:
        cliente: Client with the demo access mounted.
        usuarios_semilla: Rows served by the double.
    """
    usuarios_semilla["movalle"].role = "operativo"

    cuerpo = cliente.post(RUTA_DEMO, json={"rol": "admin"}).json()

    claims = jwt.decode(
        cuerpo["access_token"], MINIMAL_ENV["JWT_SECRET_KEY"], algorithms=["HS256"]
    )
    assert claims["sub"] == "movalle"
    assert claims["scope"] == "operativo"


def test_usuario_canonico_deshabilitado_no_emite_token(
    cliente: TestClient, usuarios_semilla: dict[str, AppUser]
) -> None:
    """A disabled canonical user gets the neutral 401, not a session.

    Args:
        cliente: Client with the demo access mounted.
        usuarios_semilla: Rows served by the double.
    """
    usuarios_semilla["dhernandez"].disabled = True

    respuesta = cliente.post(RUTA_DEMO, json={"rol": "analista"})

    assert respuesta.status_code == 401
    assert respuesta.json()["codigo"] == "credenciales_invalidas"


def test_sin_la_migracion_no_hay_demostracion(
    cliente: TestClient, usuarios_semilla: dict[str, AppUser]
) -> None:
    """With an empty table the door answers 401 instead of failing with a 500.

    Args:
        cliente: Client with the demo access mounted.
        usuarios_semilla: Rows served by the double, emptied here.
    """
    usuarios_semilla.clear()

    assert cliente.post(RUTA_DEMO, json={"rol": "operativo"}).status_code == 401


def test_el_token_de_demostracion_abre_la_sesion(cliente: TestClient) -> None:
    """The demo token is a real session: it is accepted by ``/api/auth/me``.

    Args:
        cliente: Client with the demo access mounted.
    """
    token = cliente.post(RUTA_DEMO, json={"rol": "directivo"}).json()["access_token"]

    respuesta = cliente.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["role"] == "directivo"
