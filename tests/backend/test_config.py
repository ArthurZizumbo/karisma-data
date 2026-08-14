"""Tests for the strict settings contract (CA-8).

The application must refuse to start when ``DATABASE_URL``, ``JWT_SECRET_KEY``
or ``GEMINI_API_KEY`` is missing. This rule is non-negotiable: relaxing it is
what turns a missing secret into a runtime surprise.

The ``app`` package is imported inside every test, after the path bootstrap of
``conftest.py`` has run, exactly as the fixtures do.
"""

import pytest
from conftest import MINIMAL_ENV
from pydantic import ValidationError

REQUIRED_VARIABLES = ("DATABASE_URL", "JWT_SECRET_KEY", "GEMINI_API_KEY")


@pytest.mark.parametrize("missing", REQUIRED_VARIABLES)
def test_config_estricta_falla_sin_variables(
    monkeypatch: pytest.MonkeyPatch,
    missing: str,
) -> None:
    """Dropping any required variable raises a validation error.

    ``_env_file=None`` disables dotenv loading so the assertion depends only on
    the process environment, never on a file of the developer machine.

    Args:
        monkeypatch: Fixture used to remove the variable under test.
        missing: Name of the environment variable removed for this case.
    """
    from app.core.config import Settings

    monkeypatch.delenv(missing, raising=False)

    with pytest.raises(ValidationError) as error:
        # pydantic-settings accepts _env_file at runtime, but it does not show
        # up in the __init__ that pydantic synthesises from the fields, so mypy
        # does not know about it. Same reason as the ignore on get_settings().
        Settings(_env_file=None)  # type: ignore[call-arg]

    assert missing.lower() in str(error.value)


def test_config_carga_completa() -> None:
    """With the three variables present the settings expose their values."""
    from app.core.config import get_settings

    settings = get_settings()

    # Compared against the fixture itself: duplicating the values here made this
    # test fail for the wrong reason the moment the fixture changed.
    assert settings.database_url == MINIMAL_ENV["DATABASE_URL"]
    assert settings.jwt_secret_key == MINIMAL_ENV["JWT_SECRET_KEY"]
    assert settings.gemini_api_key == MINIMAL_ENV["GEMINI_API_KEY"]
    assert settings.app_env == MINIMAL_ENV["APP_ENV"]
    assert settings.log_level == MINIMAL_ENV["LOG_LEVEL"]
    assert get_settings() is settings


def test_app_no_arranca_sin_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """The application factory itself aborts when a secret is missing.

    Args:
        monkeypatch: Fixture used to clear the required variables.
    """
    from app.core.config import get_settings
    from app.main import create_app

    for name in REQUIRED_VARIABLES:
        monkeypatch.delenv(name, raising=False)
    get_settings.cache_clear()

    with pytest.raises(ValidationError):
        create_app()


def test_config_usa_valores_por_defecto(monkeypatch: pytest.MonkeyPatch) -> None:
    """Optional variables fall back to the documented defaults.

    Args:
        monkeypatch: Fixture used to clear the optional variables.
    """
    from app.core.config import Settings

    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.app_env == "local"
    assert settings.log_level == "INFO"


def test_config_rechaza_clave_de_firma_corta(monkeypatch: pytest.MonkeyPatch) -> None:
    """A signing key shorter than the digest it feeds must abort the startup."""
    from pydantic import ValidationError

    from app.core.config import get_settings

    monkeypatch.setenv("JWT_SECRET_KEY", "corta")
    get_settings.cache_clear()

    with pytest.raises(ValidationError):
        get_settings()


def test_config_rechaza_marcador_fuera_de_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A placeholder secret is allowed in ``local`` and rejected anywhere else.

    Only ``GEMINI_API_KEY`` is exercised here: every placeholder is shorter than
    the 32 character floor, so on ``JWT_SECRET_KEY`` the length rule fires first
    and this branch would never be the reason for the failure.

    Args:
        monkeypatch: Fixture used to patch the environment.
    """
    from app.core.config import get_settings

    monkeypatch.setenv("GEMINI_API_KEY", "pendiente-us-020")

    monkeypatch.setenv("APP_ENV", "prod")
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        get_settings()

    monkeypatch.setenv("APP_ENV", "local")
    get_settings.cache_clear()
    assert get_settings().gemini_api_key == "pendiente-us-020"
