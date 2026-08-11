"""Tests for what authentication is allowed to write to the log.

Two rules, and a third case that keeps the first two honest. A password or a
token in a record survives the request that produced it, gets shipped to the log
sink and outlives the session; and the identifier typed in a failed attempt is
where a password ends up when somebody misses the field. The third case asserts
that the successful login does record something useful, so that a module which
simply stopped logging could not pass this file.

The module logger is replaced by a capturing double instead of reconfiguring
structlog: ``create_app`` caches the bound logger on first use, so a global
reconfiguration would or would not take effect depending on the order of the
suite, and a privacy test that depends on test ordering is worse than none.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import structlog

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

CONTRASENA_TECLEADA = "contrasena-que-nunca-debe-aparecer"
USUARIO_INEXISTENTE = "usuario-que-no-existe"
USUARIO = "lmendez"


@pytest.fixture
def registro(monkeypatch: pytest.MonkeyPatch) -> structlog.testing.CapturingLogger:
    """Replace the logger of the authentication service with a capturing double.

    Args:
        monkeypatch: Used to swap the module level logger.

    Returns:
        The double, whose ``calls`` list holds every emitted record.
    """
    from app.services import auth_service

    capturador = structlog.testing.CapturingLogger()
    monkeypatch.setattr(auth_service, "logger", capturador)
    return capturador


def texto_registrado(registro: structlog.testing.CapturingLogger) -> str:
    """Return every captured record flattened into a single searchable string.

    Args:
        registro: The capturing double.

    Returns:
        The concatenation of the arguments of every call.
    """
    return " ".join(repr(llamada) for llamada in registro.calls)


def test_el_registro_no_contiene_la_contrasena_ni_el_token(
    cliente: TestClient, registro: structlog.testing.CapturingLogger
) -> None:
    """Neither the successful login nor the failed one records a credential.

    Args:
        cliente: Client bound to the repository double.
        registro: Capturing double of the service logger.
    """
    from conftest import CONTRASENA_DE_PRUEBA

    token = cliente.post(
        "/api/auth/token",
        data={"username": USUARIO, "password": CONTRASENA_DE_PRUEBA},
    ).json()["access_token"]
    cliente.post(
        "/api/auth/token",
        data={"username": USUARIO, "password": CONTRASENA_TECLEADA},
    )

    registrado = texto_registrado(registro)

    assert CONTRASENA_DE_PRUEBA not in registrado
    assert CONTRASENA_TECLEADA not in registrado
    assert token not in registrado


def test_el_usuario_inexistente_no_se_registra_por_nombre(
    cliente: TestClient, registro: structlog.testing.CapturingLogger
) -> None:
    """A failed attempt never records the identifier that was typed.

    Args:
        cliente: Client bound to the repository double.
        registro: Capturing double of the service logger.
    """
    cliente.post(
        "/api/auth/token",
        data={"username": USUARIO_INEXISTENTE, "password": CONTRASENA_TECLEADA},
    )

    registrado = texto_registrado(registro)

    assert registro.calls, "el fallo no registro absolutamente nada"
    assert USUARIO_INEXISTENTE not in registrado


def test_el_acceso_concedido_si_registra_usuario_y_rol(
    cliente: TestClient, registro: structlog.testing.CapturingLogger
) -> None:
    """A successful login is auditable: it records who entered and as what.

    Args:
        cliente: Client bound to the repository double.
        registro: Capturing double of the service logger.
    """
    from conftest import CONTRASENA_DE_PRUEBA

    cliente.post(
        "/api/auth/token",
        data={"username": USUARIO, "password": CONTRASENA_DE_PRUEBA},
    )

    concedidos = [
        llamada for llamada in registro.calls if llamada.args == ("acceso_concedido",)
    ]

    assert len(concedidos) == 1
    assert concedidos[0].kwargs == {"usuario": USUARIO, "rol": "operativo"}
