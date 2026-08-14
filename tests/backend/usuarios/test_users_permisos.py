"""The 401 and the 403 of the three administration endpoints, by role.

The subject is not the router: it is the security dependency the router
declares. Three defects put these cases in red, and every one of them has been
committed before in some project. Declaring the caller with
``Depends(get_current_user)`` instead of ``Security(...)`` mounts the endpoint
with no scope requirement and leaves the whole user list readable by any
session. Writing ``scopes=[]`` to unblock a demo does the same thing more
explicitly. And inverting the hierarchy would let an operator change roles.

The parametrization walks the three roles that must not reach the module and
the three operations, nine cases, because the rule is not "the endpoint is
protected" but "each of these three verbs is protected".
"""

import uuid
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Final

import pytest
from fastapi.testclient import TestClient

from app.core.scopes import ErrorCode, Scope

if TYPE_CHECKING:
    from app.models.user import AppUser

from .conftest import OTRO

# The three live operations of the module, with a body that is valid where the
# contract demands one: an invalid body would be rejected before the security
# dependency runs and the case would prove nothing about permissions.
OPERACIONES: Final[tuple[tuple[str, str, dict[str, Any] | None], ...]] = (
    ("GET", "/api/users", None),
    ("PATCH", "/api/users/{user_id}", {"role": Scope.OPERATIVO.value}),
    ("DELETE", "/api/users/{user_id}", None),
)

SIN_PERMISO: Final[tuple[Scope, ...]] = (
    Scope.OPERATIVO,
    Scope.ANALISTA,
    Scope.DIRECTIVO,
)

IDS_OPERACION: Final[list[str]] = [
    f"{metodo} {ruta}" for metodo, ruta, _ in OPERACIONES
]


@pytest.mark.parametrize(("metodo", "ruta", "cuerpo"), OPERACIONES, ids=IDS_OPERACION)
def test_sin_token_responde_401_con_desafio_bearer(
    cliente_admin: TestClient,
    id_de: Callable[[str], uuid.UUID],
    metodo: str,
    ruta: str,
    cuerpo: dict[str, Any] | None,
) -> None:
    """An anonymous request is refused with the RFC 6750 challenge."""
    respuesta = cliente_admin.request(
        metodo, ruta.format(user_id=id_de(OTRO)), json=cuerpo
    )

    assert respuesta.status_code == 401
    assert respuesta.headers["WWW-Authenticate"].startswith("Bearer ")
    assert respuesta.json()["detail"] == ErrorCode.CREDENCIALES_AUSENTES.value


@pytest.mark.parametrize(("metodo", "ruta", "cuerpo"), OPERACIONES, ids=IDS_OPERACION)
@pytest.mark.parametrize("rol", SIN_PERMISO, ids=[rol.value for rol in SIN_PERMISO])
def test_rol_sin_admin_responde_403(
    cliente_admin: TestClient,
    cabecera_de: Callable[[Scope], dict[str, str]],
    id_de: Callable[[str], uuid.UUID],
    rol: Scope,
    metodo: str,
    ruta: str,
    cuerpo: dict[str, Any] | None,
) -> None:
    """A valid session below ``admin`` is refused with 403, never with 404."""
    respuesta = cliente_admin.request(
        metodo,
        ruta.format(user_id=id_de(OTRO)),
        json=cuerpo,
        headers=cabecera_de(rol),
    )

    assert respuesta.status_code == 403
    assert respuesta.json()["detail"] == ErrorCode.PERMISOS_INSUFICIENTES.value


@pytest.mark.parametrize(("metodo", "ruta", "cuerpo"), OPERACIONES, ids=IDS_OPERACION)
def test_admin_atraviesa_las_tres_operaciones(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    id_de: Callable[[str], uuid.UUID],
    metodo: str,
    ruta: str,
    cuerpo: dict[str, Any] | None,
) -> None:
    """The administrator is served, so the 403 above is about the role."""
    respuesta = cliente_admin.request(
        metodo,
        ruta.format(user_id=id_de(OTRO)),
        json=cuerpo,
        headers=cabecera_admin,
    )

    assert respuesta.status_code == 200


def test_sesion_revocada_no_alcanza_el_modulo(
    cliente_admin: TestClient,
    cabecera_admin: dict[str, str],
    usuarios_semilla: "dict[str, AppUser]",
) -> None:
    """A disabled administrator is refused before any business rule runs.

    This is what makes the "re-enabling yourself" branch unreachable, and it is
    why the service does not special case it: without this 401 the branch would
    be dead code with a test that cannot fail.
    """
    usuarios_semilla["movalle"].disabled = True

    respuesta = cliente_admin.get("/api/users", headers=cabecera_admin)

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == ErrorCode.SESION_REVOCADA.value
