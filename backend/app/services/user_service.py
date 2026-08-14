"""Read access to ``app_user``, behind a protocol the tests can substitute.

The protocol is not ceremony. It is what lets the whole authentication suite run
without PostgreSQL, keeping the property US-002 established -no test opens a
connection- while still exercising the 401, the 403 and the disabled user.
``get_user_repository`` is the seam: tests and the permission matrix of US-016
override that dependency, never the engine.
"""

import uuid
from collections.abc import Sequence
from typing import Annotated, Any, Final, Protocol

from fastapi import Depends
from sqlalchemy import Executable, Row, func, update
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.scopes import Scope
from app.models.user import AppUser, UserAdminOut


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


# The eight columns the administration side is allowed to read, named one by
# one. This is the deepest of the four locks against leaking the digest: what is
# never selected cannot be serialised, not by a stray mapping, not by a debug
# dump and not by a misplaced response_model.
_ADMIN_COLUMNS: Final[tuple[Any, ...]] = (
    col(AppUser.id),
    col(AppUser.username),
    col(AppUser.email),
    col(AppUser.full_name),
    col(AppUser.role),
    col(AppUser.disabled),
    col(AppUser.created_at),
    col(AppUser.updated_at),
)


class AdminUserRepository(Protocol):
    """Administration side of ``app_user``. Separate from ``UserRepository``.

    Widening the authentication protocol would break the fake repository US-015
    wired into ``tests/backend/conftest.py``, a file this module does not ask
    anybody to open. Two protocols over one table is interface segregation
    applied for a reason, and the return type is the second lock against the
    digest: this side never hands an ``AppUser`` upwards.
    """

    async def list_page(
        self, *, limit: int, offset: int
    ) -> tuple[Sequence[UserAdminOut], int]:
        """Return one page of users and the size of the whole table.

        Args:
            limit: Page size.
            offset: Rows skipped before the page.

        Returns:
            The page, ordered by ``username`` ascending, and the total number of
            rows in the table -not in the page-.
        """
        ...

    async def get_by_id(self, user_id: uuid.UUID) -> UserAdminOut | None:
        """Return one user by primary key.

        Args:
            user_id: Primary key of the row.

        Returns:
            The user, or ``None`` when no row carries that identifier.
        """
        ...

    async def update_role(self, user_id: uuid.UUID, role: Scope) -> UserAdminOut | None:
        """Write the new role of a user and stamp the modification.

        Args:
            user_id: Primary key of the row.
            role: Role to store.

        Returns:
            The updated user, or ``None`` when no row carries that identifier.
        """
        ...

    async def set_disabled(
        self, user_id: uuid.UUID, disabled: bool
    ) -> UserAdminOut | None:
        """Write the soft delete flag of a user and stamp the modification.

        Args:
            user_id: Primary key of the row.
            disabled: New value of the flag.

        Returns:
            The updated user, or ``None`` when no row carries that identifier.
        """
        ...


class SqlAdminUserRepository:
    """PostgreSQL implementation. The only place that writes ``app_user``.

    Every statement projects the columns of ``_ADMIN_COLUMNS`` and never selects
    ``hashed_password``. Both mutating methods set ``updated_at`` in the same
    statement that changes the row, so no trigger is needed and the write stays
    visible in the code that performs it, which is what the prose of the
    migration argues for.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Bind the repository to the session of the current request.

        Args:
            session: Session yielded by ``get_session``.
        """
        self._session = session

    async def list_page(
        self, *, limit: int, offset: int
    ) -> tuple[Sequence[UserAdminOut], int]:
        """Return one page of users and the size of the whole table.

        The window is cut by the database with ``LIMIT`` and ``OFFSET``, and the
        total comes from its own ``COUNT``: slicing in Python after reading the
        table would make the page a lie about the cost, and counting the page
        would make ``total`` a lie about the table.

        Args:
            limit: Page size.
            offset: Rows skipped before the page.

        Returns:
            The page, ordered by ``username`` ascending, and the total number of
            rows in the table.
        """
        page = (
            select(*_ADMIN_COLUMNS)
            .order_by(col(AppUser.username))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(page)
        items = [_to_user_admin_out(row) for row in result.all()]

        total = await self._session.scalar(select(func.count()).select_from(AppUser))
        return items, int(total or 0)

    async def get_by_id(self, user_id: uuid.UUID) -> UserAdminOut | None:
        """Return one user by primary key.

        Args:
            user_id: Primary key of the row.

        Returns:
            The user, or ``None`` when no row carries that identifier.
        """
        statement = select(*_ADMIN_COLUMNS).where(col(AppUser.id) == user_id)
        result = await self._session.execute(statement)
        row = result.first()
        return None if row is None else _to_user_admin_out(row)

    async def update_role(self, user_id: uuid.UUID, role: Scope) -> UserAdminOut | None:
        """Write the new role of a user and stamp the modification.

        Args:
            user_id: Primary key of the row.
            role: Role to store, as the canonical literal of ``Scope``.

        Returns:
            The updated user, or ``None`` when no row carries that identifier.
        """
        statement = (
            update(AppUser)
            .where(col(AppUser.id) == user_id)
            .values(role=role.value, updated_at=func.now())
            .returning(*_ADMIN_COLUMNS)
        )
        return await self._write(statement)

    async def set_disabled(
        self, user_id: uuid.UUID, disabled: bool
    ) -> UserAdminOut | None:
        """Write the soft delete flag of a user and stamp the modification.

        The row is never deleted: ``db/AGENTS.md`` forbids a physical delete of
        a user precisely so the account keeps existing after the access is cut.

        Args:
            user_id: Primary key of the row.
            disabled: New value of the flag.

        Returns:
            The updated user, or ``None`` when no row carries that identifier.
        """
        statement = (
            update(AppUser)
            .where(col(AppUser.id) == user_id)
            .values(disabled=disabled, updated_at=func.now())
            .returning(*_ADMIN_COLUMNS)
        )
        return await self._write(statement)

    async def _write(self, statement: Executable) -> UserAdminOut | None:
        """Run a returning update and commit only when it matched a row.

        Args:
            statement: ``UPDATE ... RETURNING`` over ``app_user``.

        Returns:
            The updated user, or ``None`` when the statement matched nothing.
        """
        result = await self._session.execute(statement)
        row = result.first()
        if row is None:
            return None
        await self._session.commit()
        return _to_user_admin_out(row)


def _to_user_admin_out(row: Row[Any]) -> UserAdminOut:
    """Map one projected row onto the administration response contract.

    Args:
        row: Row carrying the eight columns of ``_ADMIN_COLUMNS``, in order.

    Returns:
        The response model of that user.
    """
    user_id, username, email, full_name, role, disabled, created_at, updated_at = row
    return UserAdminOut(
        id=user_id,
        username=username,
        email=email,
        full_name=full_name,
        role=Scope(role),
        disabled=disabled,
        created_at=created_at,
        updated_at=updated_at,
    )


async def get_admin_user_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AdminUserRepository:
    """Return the administration repository bound to the session of the request.

    This is the seam the suite overrides, never the engine: the users tests run
    without PostgreSQL, which is the property US-002 established.

    Args:
        session: Session yielded by ``get_session``.

    Returns:
        The PostgreSQL implementation of the administration repository.
    """
    return SqlAdminUserRepository(session)
