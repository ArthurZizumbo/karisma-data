"""Application factory for the Karisma Data API."""

import logging

import structlog
from fastapi import FastAPI

from app.api import auth, catalog, chat, export, health, lineage, metrics, users
from app.core.config import LOCAL_ENV, get_settings
from app.core.permissions import assert_scope_coverage
from app.services.auth_service import InvalidCredentialsError
from app.services.proveedores import verificar_proveedor_declarado

logger = structlog.get_logger()


def configure_logging(log_level: str) -> None:
    """Configure structlog to emit structured JSON records.

    Args:
        log_level: Minimum severity name, for example ``INFO``. Unknown names
            fall back to ``INFO`` so that a typo never silences the service.
    """
    level = logging.getLevelNamesMapping().get(log_level.upper(), logging.INFO)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def create_app() -> FastAPI:
    """Build the FastAPI application.

    Settings are resolved first on purpose: a missing secret must abort the
    startup before any router is mounted.

    Returns:
        The configured application instance.

    Raises:
        pydantic.ValidationError: If a required environment variable is missing.
        ScopeCoverageError: If a route under ``/api`` is not governed by the
            permission policy.
        ValueError: If ``CHAT_PROVIDER`` names a provider with no factory
            behind it.
    """
    settings = get_settings()
    configure_logging(settings.log_level)

    # A CHAT_PROVIDER without a factory stops the startup here instead of
    # turning every POST /api/chat into a 500.
    verificar_proveedor_declarado(settings.chat_provider)

    # The interactive docs are the full inventory of endpoints, request schemas
    # and, from US-015 on, the security scheme. They stay on locally because
    # they are how the team explores the API, and off everywhere else.
    expose_docs = settings.app_env == LOCAL_ENV

    application = FastAPI(
        title="Karisma Data API",
        version="0.1.0",
        summary="API del Portal Centralizado de Datos Financieros",
        docs_url="/docs" if expose_docs else None,
        redoc_url="/redoc" if expose_docs else None,
        openapi_url="/openapi.json" if expose_docs else None,
    )
    application.include_router(health.router)
    application.include_router(auth.router)
    application.include_router(catalog.router)
    application.include_router(lineage.router)
    application.include_router(metrics.router)
    application.include_router(users.router)
    application.include_router(chat.router)
    application.include_router(export.router)

    # The demo access is not an endpoint with an "if" inside: it is a router
    # that is not mounted. Off, the route does not exist -404 and nothing in
    # /openapi.json- instead of a 403 that would confirm the door is there.
    if settings.demo_login_enabled:
        application.include_router(auth.demo_router)

    application.add_exception_handler(
        InvalidCredentialsError, auth.handle_invalid_credentials
    )

    # Last check before the application is usable, and deliberately before the
    # record below: a route under /api without a declared permission stops the
    # startup instead of being served open. It runs on the application already
    # built, so it sees exactly the routers this configuration mounted.
    assert_scope_coverage(application)

    logger.info(
        "application_started",
        app_env=settings.app_env,
        log_level=settings.log_level,
        demo_login_enabled=settings.demo_login_enabled,
    )
    return application


app = create_app()
