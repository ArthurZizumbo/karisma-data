"""The 401/403 matrix, seen from HTTP and parametrized by role.

The probe application of the ``conftest`` of this package mounts one route per
level with the real ``Security(get_current_user, scopes=[...])``. The endpoints
are not the subject: the subject is the authorization dependency, which is
production code, and the hierarchy behind it. The user lookup is substituted
through ``get_user_repository``, so the whole matrix runs without PostgreSQL.

The assertion of the matrix is asymmetric on purpose: a role without permission
gets exactly 403, and a role with permission gets anything that is neither 401
nor 403. That is what lets these cases interrogate endpoints written months from
now without inventing valid bodies for them, because the security dependency
raises before the body is validated.
"""

import itertools
import time
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any, Final

import jwt
import pytest
from conftest import FakeUserRepository
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.permissions import (
    PUBLIC_ROUTES,
    SCOPE_REGISTRY,
    PermissionRule,
    RouteKey,
    live_routes,
)
from app.core.scopes import ErrorCode, Scope
from app.services.user_service import get_user_repository

from .conftest import RUTA_PUBLICA, SONDAS, ruta_de

if TYPE_CHECKING:
    from app.models.user import AppUser

# Placeholder used for every path parameter of a real route. The value never
# has to exist: what is being measured is whether the request gets past the
# security dependency, and a 404 on the other side is a legitimate answer.
MARCADOR: Final[str] = "sonda"

# Signing key of the forged token of the "another signature" vector. It is long
# enough that PyJWT does not warn about the key instead of about the forgery.
CLAVE_AJENA: Final[str] = "otra-clave-de-firma-con-32-caracteres"

# Cases of the matrix: every level of the probe application against every role.
CASOS_DE_LA_MATRIZ: Final[tuple[tuple[str, Scope], ...]] = tuple(
    itertools.product(list(SONDAS), list(Scope))
)

# Rows of the policy whose route the portal already serves. They are the ones
# the matrix can interrogate today; the rest are policy published ahead of time.
FILAS_VIGENTES: Final[tuple[tuple[RouteKey, PermissionRule], ...]] = tuple(
    (clave, regla)
    for clave, regla in SCOPE_REGISTRY.items()
    if regla.status == "vigente"
)


def _alcanza(rol: Scope, nivel: str) -> bool:
    """Report whether a role reaches the level of a probe.

    Args:
        rol: Role carried by the token.
        nivel: Key of ``SONDAS``.

    Returns:
        ``True`` when the request must not be rejected.
    """
    exigidos = SONDAS[nivel]
    return not exigidos or list(Scope).index(rol) >= max(
        list(Scope).index(scope) for scope in exigidos
    )


def _url_de(clave: RouteKey) -> str:
    """Fill the path parameters of a route template with the placeholder.

    Args:
        clave: Route of the policy.

    Returns:
        A concrete path the client can request.
    """
    partes = [
        MARCADOR if segmento.startswith("{") else segmento
        for segmento in clave.path.split("/")
    ]
    return "/".join(partes)


def _pedir(cliente: TestClient, clave: RouteKey, token: str | None) -> int:
    """Send a request to a route of the policy and return its status.

    Args:
        cliente: Client of the application under test.
        clave: Route of the policy.
        token: Encoded token, or ``None`` for an anonymous request.

    Returns:
        The status code of the answer.
    """
    cabeceras = {"Authorization": f"Bearer {token}"} if token else {}
    respuesta = cliente.request(clave.method, _url_de(clave), headers=cabeceras)
    return int(respuesta.status_code)


@pytest.mark.parametrize("nivel", list(SONDAS))
def test_401_sin_token(cliente_de_sonda: TestClient, nivel: str) -> None:
    """An anonymous request never reaches the endpoint, at any level.

    With ``auto_error=False`` and no challenge of our own the request would run
    the endpoint with no credentials at all, which is failing open.

    Args:
        cliente_de_sonda: Client of the probe application.
        nivel: Level of the probe under test.
    """
    respuesta = cliente_de_sonda.get(ruta_de(nivel))

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == ErrorCode.CREDENCIALES_AUSENTES.value


def test_la_ruta_sin_seguridad_de_la_sonda_responde_anonima(
    cliente_de_sonda: TestClient,
) -> None:
    """The 401 comes from the dependency and not from something global.

    Without this the previous test would also pass in an application that
    rejects every anonymous request for an unrelated reason.

    Args:
        cliente_de_sonda: Client of the probe application.
    """
    respuesta = cliente_de_sonda.get(RUTA_PUBLICA)

    assert respuesta.status_code == 200


@pytest.mark.parametrize(
    ("vector", "esperado"),
    [
        ("firma_ajena", ErrorCode.CREDENCIALES_INVALIDAS),
        ("alg_none", ErrorCode.CREDENCIALES_INVALIDAS),
        ("cabecera_malformada", ErrorCode.CREDENCIALES_AUSENTES),
        ("bearer_vacio", ErrorCode.CREDENCIALES_INVALIDAS),
        ("sin_reclamacion_scope", ErrorCode.CREDENCIALES_INVALIDAS),
    ],
)
def test_401_token_manipulado(
    cliente_de_sonda: TestClient,
    token_de: Callable[..., str],
    usuario_por_rol: dict[Scope, str],
    vector: str,
    esperado: ErrorCode,
) -> None:
    """A forged credential is rejected before the hierarchy is even consulted.

    ``alg=none`` is the vector that matters most: without an explicit list of
    algorithms anybody mints an ``admin`` token with no key at all.

    Args:
        cliente_de_sonda: Client of the probe application.
        token_de: Factory of forged tokens.
        usuario_por_rol: Login identifier of a seeded user per role.
        vector: Way of breaking the credential.
        esperado: Code the answer must carry.
    """
    usuario = usuario_por_rol[Scope.ADMIN]
    emitido = int(time.time())
    cabeceras = {
        "firma_ajena": lambda: {
            "Authorization": f"Bearer {token_de(usuario, clave=CLAVE_AJENA)}"
        },
        "alg_none": lambda: {
            "Authorization": "Bearer "
            + jwt.encode(
                {
                    "sub": usuario,
                    "scope": Scope.ADMIN.value,
                    "iat": emitido,
                    "exp": emitido + 60,
                },
                None,
                algorithm="none",
            )
        },
        "cabecera_malformada": lambda: {"Authorization": f"Token {token_de(usuario)}"},
        "bearer_vacio": lambda: {"Authorization": "Bearer "},
        "sin_reclamacion_scope": lambda: {
            "Authorization": f"Bearer {token_de(usuario, con_scope=False)}"
        },
    }[vector]()

    respuesta = cliente_de_sonda.get(ruta_de("usuarios"), headers=cabeceras)

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == esperado.value


def test_401_token_expirado(
    cliente_de_sonda: TestClient,
    token_de: Callable[..., str],
    usuario_por_rol: dict[Scope, str],
) -> None:
    """The thirty minute session ends, and nothing renews it behind the scenes.

    Args:
        cliente_de_sonda: Client of the probe application.
        token_de: Factory of forged tokens.
        usuario_por_rol: Login identifier of a seeded user per role.
    """
    token = token_de(usuario_por_rol[Scope.ADMIN], Scope.ADMIN.value, vida_segundos=-1)

    respuesta = cliente_de_sonda.get(
        ruta_de("usuarios"), headers={"Authorization": f"Bearer {token}"}
    )

    assert respuesta.status_code == 401
    assert respuesta.json()["detail"] == ErrorCode.SESION_EXPIRADA.value


@pytest.mark.parametrize("nivel", list(SONDAS))
def test_401_lleva_www_authenticate(cliente_de_sonda: TestClient, nivel: str) -> None:
    """Every 401 carries the challenge, and it names the level when there is one.

    The header is a literal acceptance criterion of the US, and the ``scope=``
    parameter is what tells a conforming client what to ask for.

    Args:
        cliente_de_sonda: Client of the probe application.
        nivel: Level of the probe under test.
    """
    respuesta = cliente_de_sonda.get(ruta_de(nivel))
    reto = respuesta.headers["www-authenticate"]

    assert reto.startswith('Bearer realm="karisma"')
    for scope in SONDAS[nivel]:
        assert f'scope="{scope.value}"' in reto
    if not SONDAS[nivel]:
        assert "scope=" not in reto


@pytest.mark.parametrize(("nivel", "rol"), CASOS_DE_LA_MATRIZ, ids=str)
def test_matriz_por_rol_en_la_app_de_sonda(
    cliente_de_sonda: TestClient,
    token_de_rol: Callable[[Scope], str],
    nivel: str,
    rol: Scope,
) -> None:
    """Every role against every level, seen from HTTP.

    This is where a hierarchy written backwards shows up as what it is: an
    ``operativo`` exporting, an ``analista`` administering users, or a
    ``directivo`` locked out of his own summary.

    Args:
        cliente_de_sonda: Client of the probe application.
        token_de_rol: Factory of valid tokens per role.
        nivel: Level of the probe under test.
        rol: Role carried by the token.
    """
    respuesta = cliente_de_sonda.get(
        ruta_de(nivel), headers={"Authorization": f"Bearer {token_de_rol(rol)}"}
    )

    if _alcanza(rol, nivel):
        assert respuesta.status_code not in {401, 403}
    else:
        assert respuesta.status_code == 403
        assert respuesta.json()["detail"] == ErrorCode.PERMISOS_INSUFICIENTES.value


@pytest.mark.parametrize("nivel", ["agregacion", "resumen", "usuarios"])
def test_403_no_revela_nada(
    cliente_de_sonda: TestClient,
    token_de_rol: Callable[[Scope], str],
    usuario_por_rol: dict[Scope, str],
    nivel: str,
) -> None:
    """The denial says the code and nothing else: no resource, no identity.

    Args:
        cliente_de_sonda: Client of the probe application.
        token_de_rol: Factory of valid tokens per role.
        usuario_por_rol: Login identifier of a seeded user per role.
        nivel: Level of the probe under test.
    """
    respuesta = cliente_de_sonda.get(
        ruta_de(nivel),
        headers={"Authorization": f"Bearer {token_de_rol(Scope.OPERATIVO)}"},
    )
    cuerpo: dict[str, Any] = respuesta.json()

    assert respuesta.status_code == 403
    assert set(cuerpo) == {"detail"}
    assert cuerpo["detail"] == ErrorCode.PERMISOS_INSUFICIENTES.value
    texto = respuesta.text
    assert nivel not in texto
    assert usuario_por_rol[Scope.OPERATIVO] not in texto
    assert 'error="insufficient_scope"' in respuesta.headers["www-authenticate"]


def test_usuario_desactivado_es_401_aunque_su_rol_alcance(
    cliente_de_sonda: TestClient,
    token_de_rol: Callable[[Scope], str],
    usuario_por_rol: dict[Scope, str],
    usuarios_semilla: dict[str, "AppUser"],
) -> None:
    """The soft delete of US-018 takes effect on the very next request.

    The role of the caller reaches the endpoint, so a 200 here would mean the
    disabled flag is read after the scopes or not read at all. The answer is a
    401 and not a 403 on purpose: the frontend has to re-login, not stare at a
    session it believes alive.

    Args:
        cliente_de_sonda: Client of the probe application.
        token_de_rol: Factory of valid tokens per role.
        usuario_por_rol: Login identifier of a seeded user per role.
        usuarios_semilla: Rows served by the repository double.
    """
    cabeceras = {"Authorization": f"Bearer {token_de_rol(Scope.ADMIN)}"}
    antes = cliente_de_sonda.get(ruta_de("usuarios"), headers=cabeceras)

    usuarios_semilla[usuario_por_rol[Scope.ADMIN]].disabled = True
    despues = cliente_de_sonda.get(ruta_de("usuarios"), headers=cabeceras)

    assert antes.status_code == 200
    assert despues.status_code == 401
    assert despues.json()["detail"] == ErrorCode.SESION_REVOCADA.value


@pytest.fixture
def aplicacion_real(
    crear_aplicacion: Callable[..., FastAPI], repositorio_falso: FakeUserRepository
) -> FastAPI:
    """Return the real application with the repository double injected.

    The demo access is mounted so that the inventory of live routes is the
    widest the portal can serve, which is the one the coverage of the
    parametrization is measured against.

    Args:
        crear_aplicacion: Factory of real applications.
        repositorio_falso: Double injected in place of the SQL repository.

    Returns:
        The application of the portal, ready to be requested.
    """
    aplicacion = crear_aplicacion(demo=True)
    aplicacion.dependency_overrides[get_user_repository] = lambda: repositorio_falso
    return aplicacion


@pytest.fixture
def cliente_real(aplicacion_real: FastAPI) -> Iterator[TestClient]:
    """Return a started client of the real application.

    Args:
        aplicacion_real: Application of the portal.

    Yields:
        A client that runs the startup and shutdown handlers.
    """
    with TestClient(aplicacion_real) as cliente:
        yield cliente


@pytest.mark.parametrize(
    ("clave", "regla"), FILAS_VIGENTES, ids=lambda valor: str(valor)
)
@pytest.mark.parametrize("rol", list(Scope))
def test_matriz_por_rol_en_la_app_real(
    cliente_real: TestClient,
    token_de_rol: Callable[[Scope], str],
    clave: RouteKey,
    regla: PermissionRule,
    rol: Scope,
) -> None:
    """Every live row of the policy, interrogated with every role.

    The path parameters are filled with a placeholder and the body goes empty:
    the security dependency answers before either is looked at, so a 422 or a
    404 from a role that does have permission is a legitimate answer and says
    nothing about authorization.

    Args:
        cliente_real: Client of the real application.
        token_de_rol: Factory of valid tokens per role.
        clave: Route of the policy.
        regla: Rule declared for that route.
        rol: Role carried by the token.
    """
    estado = _pedir(cliente_real, clave, token_de_rol(rol))
    alcanza = not regla.scopes or list(Scope).index(rol) >= max(
        list(Scope).index(scope) for scope in regla.scopes
    )

    if alcanza:
        assert estado not in {401, 403}
    else:
        assert estado == 403


@pytest.mark.parametrize("clave", [clave for clave, _ in FILAS_VIGENTES], ids=str)
def test_401_sin_token_en_la_app_real(
    cliente_real: TestClient, clave: RouteKey
) -> None:
    """Every governed route of the portal rejects the anonymous request.

    Args:
        cliente_real: Client of the real application.
        clave: Route of the policy.
    """
    assert _pedir(cliente_real, clave, None) == 401


def test_la_parametrizacion_cubre_toda_ruta_viva(aplicacion_real: FastAPI) -> None:
    """Every live governed route is one of the cases above, and no row lies.

    This is the test that makes the matrix grow by itself, and it reads in both
    directions. The day US-008 mounts ``/api/catalog/search``, its row has to
    move to ``vigente`` or this test goes red, and the endpoint would otherwise
    be served without ever being interrogated by role. A row marked ``vigente``
    whose route nobody mounted fails the same way, because a policy that
    describes routes that do not exist stops being readable.

    Args:
        aplicacion_real: Application of the portal, with the demo access on.
    """
    interrogadas = {clave for clave, _ in FILAS_VIGENTES}
    vivas = set(live_routes(aplicacion_real)) - PUBLIC_ROUTES

    assert vivas == interrogadas
