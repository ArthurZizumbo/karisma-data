"""Tests for ``POST /api/auth/token``: the shape of the token and the neutral 401.

The ``app`` package is imported inside every test, after the path bootstrap of
``conftest.py`` has run, exactly as the fixtures do. Type annotations reference
it under ``TYPE_CHECKING`` only, which costs nothing at runtime.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import jwt
import pytest
from conftest import CONTRASENA_DE_PRUEBA, MINIMAL_ENV

if TYPE_CHECKING:
    import httpx
    from conftest import FakeUserRepository
    from fastapi.testclient import TestClient

    from app.models.user import AppUser

RUTA_TOKEN = "/api/auth/token"
RUTA_ME = "/api/auth/me"
USUARIO = "lmendez"
SEGUNDOS_DE_VIDA = 1800


def solicitar_token(
    cliente: TestClient, username: str, password: str
) -> httpx.Response:
    """Post the OAuth 2.0 password form and return the raw response.

    Args:
        cliente: Client bound to the repository double.
        username: Login identifier sent in the form.
        password: Password sent in the form.

    Returns:
        The HTTP response, so each test asserts on what it cares about.
    """
    # The deprecation shim of the test client hides the return type behind Any,
    # so the annotation is what keeps the helper typed for its callers.
    respuesta: httpx.Response = cliente.post(
        RUTA_TOKEN, data={"username": username, "password": password}
    )
    return respuesta


def test_login_correcto_emite_token(cliente: TestClient) -> None:
    """A valid credential returns a bearer token.

    Args:
        cliente: Client bound to the repository double.
    """
    respuesta = solicitar_token(cliente, USUARIO, CONTRASENA_DE_PRUEBA)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["token_type"] == "bearer"
    assert cuerpo["access_token"]


def test_el_token_lleva_sub_scope_y_expiracion_de_30_minutos(
    cliente: TestClient,
) -> None:
    """The token carries exactly four claims and lasts exactly 30 minutes.

    Args:
        cliente: Client bound to the repository double.
    """
    token = solicitar_token(cliente, USUARIO, CONTRASENA_DE_PRUEBA).json()[
        "access_token"
    ]

    assert jwt.get_unverified_header(token)["alg"] == "HS256"
    claims = jwt.decode(token, MINIMAL_ENV["JWT_SECRET_KEY"], algorithms=["HS256"])
    assert set(claims) == {"sub", "scope", "iat", "exp"}
    assert claims["sub"] == USUARIO
    assert claims["scope"] == "operativo"
    assert claims["exp"] - claims["iat"] == SEGUNDOS_DE_VIDA


def test_la_respuesta_no_contiene_el_hash_del_usuario(cliente: TestClient) -> None:
    """The response body never leaks the stored digest.

    Args:
        cliente: Client bound to the repository double.
    """
    respuesta = solicitar_token(cliente, USUARIO, CONTRASENA_DE_PRUEBA)

    assert "argon2" not in respuesta.text
    assert "hashed_password" not in respuesta.text


def test_los_tres_fallos_son_indistinguibles(
    cliente: TestClient, usuarios_semilla: dict[str, AppUser]
) -> None:
    """Unknown user, wrong password and disabled account answer identically.

    Args:
        cliente: Client bound to the repository double.
        usuarios_semilla: Rows served by the double; one of them is disabled
            here to reproduce the third failure.
    """
    usuarios_semilla["eruiz"].disabled = True

    respuestas = [
        solicitar_token(cliente, "nadie", CONTRASENA_DE_PRUEBA),
        solicitar_token(cliente, USUARIO, "otra-contrasena"),
        solicitar_token(cliente, "eruiz", CONTRASENA_DE_PRUEBA),
    ]

    assert {respuesta.status_code for respuesta in respuestas} == {401}
    assert len({respuesta.content for respuesta in respuestas}) == 1
    assert {respuesta.headers["www-authenticate"] for respuesta in respuestas} == {
        "Bearer"
    }


def test_un_digest_ilegible_falla_como_una_contrasena_equivocada(
    cliente: TestClient, usuarios_semilla: dict[str, AppUser]
) -> None:
    """A digest the hasher cannot read produces the same neutral 401 as the rest.

    The fourth member of the family above, and the one no other case reaches:
    the three failures pinned there all arrive with a readable argon2id digest.
    A row carrying a digest from another scheme -a bcrypt one migrated in, a
    truncated column, an empty string- makes pwdlib raise ``UnknownHashError``.
    Without the guard in ``verify_password`` that exception escapes the request
    and the endpoint answers 500, which sits next to a 401 as a user
    enumeration oracle: the crash happens only for identifiers that exist.

    Args:
        cliente: Client bound to the repository double.
        usuarios_semilla: Rows served by the double, one of them left with a
            digest the hasher does not recognize.
    """
    usuarios_semilla[USUARIO].hashed_password = "digest-de-otro-esquema"

    ilegible = solicitar_token(cliente, USUARIO, CONTRASENA_DE_PRUEBA)
    inexistente = solicitar_token(cliente, "nadie", CONTRASENA_DE_PRUEBA)

    assert ilegible.status_code == 401
    assert ilegible.content == inexistente.content
    assert (
        ilegible.headers["www-authenticate"] == inexistente.headers["www-authenticate"]
    )


def test_el_mensaje_neutro_es_el_literal_de_la_us(cliente: TestClient) -> None:
    """The 401 carries the exact literal of the US plus its stable code.

    Args:
        cliente: Client bound to the repository double.
    """
    from app.services.auth_service import CREDENCIALES_INVALIDAS

    cuerpo = solicitar_token(cliente, "nadie", CONTRASENA_DE_PRUEBA).json()

    assert CREDENCIALES_INVALIDAS == "Credenciales incorrectas"
    assert cuerpo == {
        "detail": CREDENCIALES_INVALIDAS,
        "codigo": "credenciales_invalidas",
    }


@pytest.mark.parametrize(
    ("username", "password"),
    [
        pytest.param("nadie", CONTRASENA_DE_PRUEBA, id="usuario-inexistente"),
        pytest.param(USUARIO, "otra-contrasena", id="contrasena-incorrecta"),
    ],
)
def test_usuario_inexistente_consume_un_ciclo_de_verificacion(
    cliente: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    username: str,
    password: str,
) -> None:
    """Both failures spend exactly one verification, so they take the same time.

    Args:
        cliente: Client bound to the repository double.
        monkeypatch: Used to spy on the verification primitive.
        username: Login identifier of the failing attempt.
        password: Password of the failing attempt.
    """
    from app.core import security

    llamadas: list[str] = []
    original = security.verify_password

    def espia(plain_password: str, hashed_password: str) -> bool:
        llamadas.append(hashed_password)
        return original(plain_password, hashed_password)

    monkeypatch.setattr(security, "verify_password", espia)

    assert solicitar_token(cliente, username, password).status_code == 401
    assert len(llamadas) == 1


def test_el_formulario_es_el_estandar_de_oauth2(cliente: TestClient) -> None:
    """A JSON body is rejected: the endpoint speaks form-urlencoded.

    Sending JSON is what a client falls back to when the form parser is not
    installed, so the 422 pins the flow the Authorize button of Swagger needs.

    Args:
        cliente: Client bound to the repository double.
    """
    respuesta = cliente.post(
        RUTA_TOKEN, json={"username": USUARIO, "password": CONTRASENA_DE_PRUEBA}
    )

    assert respuesta.status_code == 422


def test_el_repositorio_recibe_el_identificador_tecleado(
    cliente: TestClient, repositorio_falso: FakeUserRepository
) -> None:
    """The login looks the user up by the identifier, never by the address.

    Args:
        cliente: Client bound to the repository double.
        repositorio_falso: Double that records every lookup.
    """
    solicitar_token(cliente, USUARIO, CONTRASENA_DE_PRUEBA)

    assert repositorio_falso.consultas == [USUARIO]


def test_cada_usuario_sembrado_entra_con_su_rol(
    cliente: TestClient, usuarios_semilla: dict[str, AppUser]
) -> None:
    """The seven seeded users sign in and carry their own role in the claim.

    Args:
        cliente: Client bound to the repository double.
        usuarios_semilla: Rows served by the double.
    """
    for username, fila in usuarios_semilla.items():
        token = solicitar_token(cliente, username, CONTRASENA_DE_PRUEBA).json()[
            "access_token"
        ]
        claims = jwt.decode(token, MINIMAL_ENV["JWT_SECRET_KEY"], algorithms=["HS256"])

        assert claims["sub"] == username
        assert claims["scope"] == fila.role


def test_un_token_recien_emitido_abre_la_sesion(cliente: TestClient) -> None:
    """The token minted by the endpoint is accepted by ``/api/auth/me``.

    Args:
        cliente: Client bound to the repository double.
    """
    token = solicitar_token(cliente, USUARIO, CONTRASENA_DE_PRUEBA).json()[
        "access_token"
    ]

    respuesta = cliente.get(RUTA_ME, headers={"Authorization": f"Bearer {token}"})

    assert respuesta.status_code == 200
    assert respuesta.json()["username"] == USUARIO
