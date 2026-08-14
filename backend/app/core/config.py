"""Application settings resolved from the process environment.

The settings object is deliberately strict: the API refuses to start when a
required secret is missing, instead of failing later with an obscure error.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
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
        chat_provider: Source that answers ``POST /api/chat``. It has a safe
            default because it is a name and not a secret: the scripted
            provider needs no credential, so an environment that never sets the
            variable still serves the assistant instead of failing to start.
            The strict rule that keeps the three credentials mandatory is
            untouched, and ``GEMINI_API_KEY`` does not become required here:
            that is the go/no-go of the Gemini provider, not this setting.
            This ``Literal`` is the vocabulary the environment may write, and
            it is **wider than what can be served**: ``gemini`` is accepted
            here so that the day the go/no-go says GO nothing but the factory
            table of ``services/proveedores`` changes. Which of these names has
            a provider behind it is decided there, and ``create_app`` refuses
            to start when the configured one has none -this module cannot ask,
            because ``core/`` does not import from ``services/``.
        data_dir: Root of the read-only data directory, where ``make data``
            leaves the synthetic silos and the preaggregated dashboard series.
            It has a default because it is a path and not a secret: the strict
            rule that keeps the three credentials mandatory is untouched.

    The four ``export_*`` settings of the background exports carry their prose
    right under their declaration instead of in this list, and that is not a
    style slip. The rule of that feature is that exactly one place of the
    backend names the storage backend -the factory that chooses the
    implementation- and a second mention here, even inside a docstring, would
    make the check that enforces it read three occurrences instead of two. All
    four keep a safe default: an environment that never exports still starts.
    """

    database_url: str
    jwt_secret_key: str = Field(min_length=MIN_SECRET_LENGTH)
    gemini_api_key: str
    app_env: str = LOCAL_ENV
    log_level: str = "INFO"
    demo_login_enabled: bool = False
    chat_provider: Literal["guionizado", "gemini"] = "guionizado"
    data_dir: Path = Path("data")

    export_storage_backend: Literal["local", "gcs"] = "local"
    """Which AlmacenDeExportaciones implementation crear_almacen returns."""

    export_signing_key: SecretStr = SecretStr("")
    """HMAC key of the local signed-link facade.

    Empty means: derive it from JWT_SECRET_KEY. It is a SecretStr so that a
    settings object dumped into a log or a traceback prints a mask.
    """

    export_link_ttl_hours: int = 24
    """Single source of the 24 hour expiry, shared by both implementations."""

    export_demo_delay_seconds: float = 0.0
    """Artificial delay that makes the in-progress moment capturable for A4."""

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

    Note:
        The message of that exception carries a truncated repr of the whole
        dotenv mapping, so it can end in a fragment of a value the model does
        not even use. Recorded as backlog entry 06 with its owner; fixing it
        here would rewrite the five assertions US-001 wrote against the
        exception type, which is not this User Story's write-set.
    """
    # The values come from the environment and from .env.local; mypy only sees
    # the dataclass-like signature synthesized from the field declarations and
    # therefore asks for them as keyword arguments.
    return Settings()  # type: ignore[call-arg]
