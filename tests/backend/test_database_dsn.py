"""Tests for the translation of the connection string and the shared engine.

One ``DATABASE_URL`` serves dbmate and SQLAlchemy. dbmate needs the plain libpq
form, and SQLAlchemy needs the driver written into the scheme: without the
translation the application starts and dies on the first login, which is the
worst moment to find out. The driver is psycopg 3, so ``sslmode`` -a libpq
parameter- survives the trip untouched; it is asyncpg, which this project does
not install, that would reject it.

Nothing here opens a connection: building an engine does not connect.
"""

from __future__ import annotations

import pytest

DSN_COMPOSE = "postgresql://karisma:karisma@db:5432/karisma?sslmode=disable"


@pytest.mark.parametrize(
    ("original", "esperado"),
    [
        pytest.param(
            DSN_COMPOSE,
            "postgresql+psycopg://karisma:karisma@db:5432/karisma?sslmode=disable",
            id="sslmode-disable-del-compose",
        ),
        pytest.param(
            "postgresql://karisma:karisma@10.0.0.5:5432/karisma?sslmode=require",
            "postgresql+psycopg://karisma:karisma@10.0.0.5:5432/karisma?sslmode=require",
            id="sslmode-require-de-cloud-sql",
        ),
        pytest.param(
            "postgresql://karisma:karisma@db:5432/karisma",
            "postgresql+psycopg://karisma:karisma@db:5432/karisma",
            id="sin-cadena-de-consulta",
        ),
        pytest.param(
            "postgresql+psycopg://karisma:karisma@db:5432/karisma?sslmode=disable",
            "postgresql+psycopg://karisma:karisma@db:5432/karisma?sslmode=disable",
            id="ya-trae-el-controlador",
        ),
    ],
)
def test_traduce_el_dsn_de_dbmate(original: str, esperado: str) -> None:
    """The scheme gains the driver and the rest of the string is preserved.

    Args:
        original: Connection string as dbmate and Compose write it.
        esperado: Connection string the psycopg dialect accepts.
    """
    from app.core.database import build_async_dsn

    assert build_async_dsn(original) == esperado


def test_un_dsn_que_no_es_de_postgres_se_rechaza() -> None:
    """A connection string for another engine fails here and not three layers on."""
    from app.core.database import build_async_dsn

    with pytest.raises(ValueError, match="PostgreSQL"):
        build_async_dsn("mysql://karisma:karisma@db:3306/karisma")


def test_el_motor_es_uno_solo_por_proceso(monkeypatch: pytest.MonkeyPatch) -> None:
    """The engine is cached: one pool per process, not one per request.

    Args:
        monkeypatch: Used to point the settings at a connection nobody opens.
    """
    from app.core.config import get_settings
    from app.core.database import get_engine

    monkeypatch.setenv("DATABASE_URL", DSN_COMPOSE)
    get_settings.cache_clear()
    get_engine.cache_clear()

    motor = get_engine()

    try:
        assert get_engine() is motor
        assert motor.url.drivername == "postgresql+psycopg"
        assert motor.url.query["sslmode"] == "disable"
    finally:
        get_engine.cache_clear()
