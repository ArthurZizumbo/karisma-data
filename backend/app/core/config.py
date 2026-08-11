"""Application settings resolved from the process environment.

The settings object is deliberately strict: the API refuses to start when a
required secret is missing, instead of failing later with an obscure error.
"""

from functools import lru_cache
from typing import Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Minimum length of the HS256 signing key, in characters. A key shorter than the
# digest it feeds adds no entropy to the signature.
MIN_SECRET_LENGTH = 32

# Values that exist only so that the strict settings can boot before the feature
# that needs the real credential. Harmless locally, unacceptable anywhere else.
DEVELOPMENT_MARKERS = frozenset({"pendiente-us-020", "changeme", "secret", "test"})

# Environment label that allows the development markers above.
LOCAL_ENV = "local"


class Settings(BaseSettings):
    """Application settings. Fails fast when required secrets are missing.

    Attributes:
        database_url: PostgreSQL connection string. Declared and validated here;
            no connection is opened by this module.
        jwt_secret_key: HS256 signing key for access tokens.
        gemini_api_key: API key used by the conversational agent.
        app_env: Deployment environment label, such as ``local`` or ``prod``.
        log_level: Minimum severity emitted by structlog.
        demo_login_enabled: Whether the credential-free demo access is mounted.
            Off by default on purpose: an environment that forgets the variable
            stays closed, and turning it on is a deliberate act written into the
            deployment.
    """

    database_url: str
    jwt_secret_key: str = Field(min_length=MIN_SECRET_LENGTH)
    gemini_api_key: str
    app_env: str = LOCAL_ENV
    log_level: str = "INFO"
    demo_login_enabled: bool = False

    model_config = SettingsConfigDict(env_file=".env.local", extra="ignore")

    @model_validator(mode="after")
    def reject_development_markers(self) -> Self:
        """Refuse to boot outside ``local`` while a placeholder secret is set.

        The strict settings guarantee that a variable is present, not that its
        value is usable. Placeholders are how this project keeps the rule honest
        before a feature lands, so they must not survive a deployment.

        Returns:
            The validated settings.

        Raises:
            ValueError: If a placeholder secret is used outside ``local``.
        """
        if self.app_env == LOCAL_ENV:
            return self
        for name, value in (
            ("JWT_SECRET_KEY", self.jwt_secret_key),
            ("GEMINI_API_KEY", self.gemini_api_key),
        ):
            if value.strip().lower() in DEVELOPMENT_MARKERS:
                message = f"{name} still holds a development placeholder"
                raise ValueError(message)
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings instance.

    The result is cached so that every caller shares the same object and the
    environment is validated only once.

    Returns:
        The validated settings.

    Raises:
        pydantic.ValidationError: If ``DATABASE_URL``, ``JWT_SECRET_KEY`` or
            ``GEMINI_API_KEY`` is missing from the environment.
    """
    # The values come from the environment and from .env.local; mypy only sees
    # the dataclass-like signature synthesized from the field declarations and
    # therefore asks for them as keyword arguments.
    return Settings()  # type: ignore[call-arg]
