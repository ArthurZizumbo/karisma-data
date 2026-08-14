"""Administration endpoints of the portal users.

Router only: it receives, delegates and answers. Every business decision lives
in ``services/user_admin_service.py`` and every scope decision in
``core/auth.py``. This module deliberately does not import ``AppUser``: without
the symbol it has no way to name the row that carries the password digest.

The security dependency is declared before the repository on purpose. The
repository hangs off ``get_session``, so an anonymous or under-privileged
request is answered without opening a database session for it.

``DELETE`` answers 200 with the updated resource and not 204: the interface
needs the new ``disabled`` and ``updated_at`` to repaint the row, and a 204
would force either a second request or a guess about what the server did.
"""

import uuid
from typing import Annotated, Final

from fastapi import APIRouter, Depends, Query, Security

from app.core.auth import get_current_user
from app.core.scopes import Scope
from app.models.user import UserAdminOut, UserOut, UserPage, UserRoleUpdate
from app.services import user_admin_service
from app.services.user_service import AdminUserRepository, get_admin_user_repository

router: Final[APIRouter] = APIRouter(prefix="/api/users", tags=["usuarios"])


@router.get("", response_model=UserPage, summary="Lista los usuarios del portal")
async def list_users_endpoint(
    current_user: Annotated[UserOut, Security(get_current_user, scopes=[Scope.ADMIN])],
    repository: Annotated[AdminUserRepository, Depends(get_admin_user_repository)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> UserPage:
    """Serve one page of the user list to an administrator.

    Args:
        current_user: Caller resolved by the security dependency. Only the
            guard matters here: an administrator sees every row, their own
            included, which is what makes the self protection rule visible.
        repository: Administration side of ``app_user``.
        limit: Page size.
        offset: Rows skipped before the page.

    Returns:
        The page, ordered by ``username`` ascending, with the total of the
        table so the interface can report what a filter is hiding.
    """
    return await user_admin_service.list_users(repository, limit=limit, offset=offset)


@router.patch(
    "/{user_id}",
    response_model=UserAdminOut,
    summary="Cambia el rol de un usuario o lo reactiva",
)
async def update_user_endpoint(
    user_id: uuid.UUID,
    body: UserRoleUpdate,
    current_user: Annotated[UserOut, Security(get_current_user, scopes=[Scope.ADMIN])],
    repository: Annotated[AdminUserRepository, Depends(get_admin_user_repository)],
) -> UserAdminOut:
    """Change the role of a user, its access flag, or both.

    Args:
        user_id: Primary key of the user being changed.
        body: Partial update. At least one of its two fields is present, which
            the model enforces before this function runs.
        current_user: Administrator running the session.
        repository: Administration side of ``app_user``.

    Returns:
        The user as it stands after the change.
    """
    return await user_admin_service.apply_partial_update(
        repository, user_id=user_id, change=body, actor=current_user
    )


@router.delete(
    "/{user_id}",
    response_model=UserAdminOut,
    summary="Desactiva un usuario por borrado logico",
)
async def disable_user_endpoint(
    user_id: uuid.UUID,
    current_user: Annotated[UserOut, Security(get_current_user, scopes=[Scope.ADMIN])],
    repository: Annotated[AdminUserRepository, Depends(get_admin_user_repository)],
) -> UserAdminOut:
    """Disable a user by logical delete. The row keeps existing.

    Args:
        user_id: Primary key of the user being disabled.
        current_user: Administrator running the session.
        repository: Administration side of ``app_user``.

    Returns:
        The user with its access already cut, so the row can be repainted
        without a second request.
    """
    return await user_admin_service.set_disabled(
        repository, user_id=user_id, disabled=True, actor=current_user
    )
