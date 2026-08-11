"""Read access to ``app_user``, behind a protocol the tests can substitute.

The protocol is not ceremony. It is what lets the whole authentication suite run
without PostgreSQL, keeping the property US-002 established -no test opens a
connection- while still exercising the 401, the 403 and the disabled user.
``get_user_repository`` is the seam: tests and the permission matrix of US-016
override that dependency, never the engine.
"""

from typing import Annotated, Protocol

from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.models.user import AppUser


class UserRepository(Protocol):
    """Read side of ``app_user`` needed by authentication."""

    async def get_by_username(self, username: str) -> AppUser | None:
        """Return the user with that login identifier.

        Args:
            username: Login identifier, as typed by the caller.

        Returns:
            The row, or ``None`` when no user carries that identifier.
        """
        ...


class SqlUserRepository:
    """PostgreSQL implementation. The only place in the module that speaks SQL."""

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to the session of the current request.

        Args:
            session: Session yielded by ``get_session``.
        """
        self._session = session

    async def get_by_username(self, username: str) -> AppUser | None:
        """Return the user with that login identifier.

        Args:
            username: Login identifier, as typed by the caller.

        Returns:
            The row, or ``None`` when no user carries that identifier.
        """
        statement = select(AppUser).where(AppUser.username == username)
        result = await self._session.exec(statement)
        return result.first()


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserRepository:
    """Return the repository bound to the session of the request.

    Args:
        session: Session yielded by ``get_session``.

    Returns:
        The PostgreSQL implementation of the repository.
    """
    return SqlUserRepository(session)
