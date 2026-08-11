"""Asynchronous access to PostgreSQL, shared by every service of the portal.

One ``DATABASE_URL`` feeds two tools with different expectations, and that is
the whole reason this module opens with a pure function. dbmate needs the plain
libpq form -``postgresql://user:pass@db:5432/karisma?sslmode=disable``- while
SQLAlchemy needs the driver written into the scheme.

The driver is **psycopg 3**, not asyncpg. The planning document of US-015 was
written against asyncpg and therefore stripped ``sslmode`` from the query
string, because asyncpg rejects libpq parameters. psycopg speaks libpq, accepts
``sslmode`` as it stands, and is already the driver in the lock file: adding
asyncpg would put a second PostgreSQL driver in the image for no gain. So the
translation is narrower than planned -it writes the driver into the scheme and
changes nothing else- and it is idempotent, so a DSN that already names the
driver survives untouched.

Nothing here connects at import time: the engine is built on first use, which
keeps ``import app.main`` free of side effects and the test suite free of
PostgreSQL.
"""

from collections.abc import AsyncIterator
from functools import lru_cache
from typing import Final

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import get_settings

# Scheme SQLAlchemy needs to load the asynchronous psycopg 3 dialect.
ASYNC_SCHEME: Final[str] = "postgresql+psycopg"

# Schemes dbmate and libpq accept for the same server.
_POSTGRES_SCHEMES: Final[frozenset[str]] = frozenset({"postgres", "postgresql"})

_SCHEME_SEPARATOR: Final[str] = "://"


def build_async_dsn(database_url: str) -> str:
    """Translate the dbmate DSN into the one the psycopg dialect accepts.

    Args:
        database_url: Connection string as dbmate and Compose already use it.

    Returns:
        The same connection string with the ``postgresql+psycopg`` scheme. The
        query string, ``sslmode`` included, is preserved: psycopg passes libpq
        parameters through.

    Raises:
        ValueError: If the value is not a PostgreSQL connection string.
    """
    scheme, separator, rest = database_url.partition(_SCHEME_SEPARATOR)
    base_scheme = scheme.split("+", 1)[0]
    if not separator or base_scheme not in _POSTGRES_SCHEMES:
        message = (
            "DATABASE_URL no es una cadena de conexion de PostgreSQL: "
            f"esquema {scheme!r}"
        )
        raise ValueError(message)

    if "+" in scheme:
        return database_url
    return f"{ASYNC_SCHEME}{_SCHEME_SEPARATOR}{rest}"


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Return the process wide engine. Lazy: importing this module opens nothing.

    The cache is what makes the pool a pool. Building one engine per request
    would open a fresh connection pool per request and exhaust the server long
    before any load test noticed.

    Returns:
        The engine bound to the translated ``DATABASE_URL``.
    """
    settings = get_settings()
    return create_async_engine(
        build_async_dsn(settings.database_url),
        # Cloud Run scales to zero and the compose database is restarted by
        # hand: without this check the first request after an idle period dies
        # on a connection the pool believes is alive.
        pool_pre_ping=True,
    )


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a session bound to the process engine. FastAPI dependency.

    Yields:
        An open session, closed when the request ends.
    """
    async with AsyncSession(get_engine(), expire_on_commit=False) as session:
        yield session
