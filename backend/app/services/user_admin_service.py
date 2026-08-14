"""Business rules of the user administration endpoints.

This module is the only place where a 404, a 409 or the 403 of a session that
outlived its role are raised, and the only authority on the self protection
rule: the interface may hide a control, but nothing outside this module decides
whether an administrator is allowed to demote or disable themselves. The
interface compares usernames because the session it holds carries no
identifier; here the comparison is against the primary key, which is the only
one a rename cannot fool.

It is also the last layer that can notice that the caller stopped being an
administrator. The scope guard of ``core/auth.py`` decides on the ``scope``
claim of the token, and that claim is a photograph of the session at the moment
it opened: it says nothing about the row as it stands now. So every write below
starts by asking ``actor.role`` -the role the database holds- and answers 403
when the row and the claim disagree.

The module never imports ``AppUser``. Without the symbol there is no way to name
the row that carries the password digest, which is the third of the four locks
that keep the hash out of every response of this API.
"""

import uuid

import structlog
from fastapi import HTTPException, status

from app.core.scopes import ErrorCode, Scope, forbidden
from app.models.user import (
    UserAdminOut,
    UserErrorCode,
    UserOut,
    UserPage,
    UserRoleUpdate,
)
from app.services.user_service import AdminUserRepository

logger = structlog.get_logger()


async def list_users(
    repository: AdminUserRepository, *, limit: int, offset: int
) -> UserPage:
    """Return one page of users ordered by username.

    Args:
        repository: Administration side of ``app_user``.
        limit: Page size, already validated by the router.
        offset: Rows skipped before the page.

    Returns:
        The page and the total number of users of the portal, so the interface
        can say how many rows a filter is hiding.
    """
    items, total = await repository.list_page(limit=limit, offset=offset)
    return UserPage(items=list(items), total=total, limit=limit, offset=offset)


async def change_role(
    repository: AdminUserRepository,
    *,
    user_id: uuid.UUID,
    role: Scope,
    actor: UserOut,
) -> UserAdminOut:
    """Change the role of a user.

    Args:
        repository: Administration side of ``app_user``.
        user_id: Primary key of the user being changed.
        role: Role to store.
        actor: Administrator running the session.

    Returns:
        The user as it stands after the change.

    Raises:
        HTTPException: 403 when the row of the caller no longer carries the
            administration role, whatever their token still claims; 404 when
            the user does not exist; 409 ``admin_no_puede_degradarse`` when the
            actor targets their own row with any role other than ``admin``.
            Targeting their own row with ``admin`` is a no-op and succeeds,
            because forbidding it would report a conflict where nothing
            changes; it is a no-op only because the check above already
            established that the caller does hold the role.
    """
    guard_actor_still_admin(actor)
    guard_self_demotion(user_id, role, actor)

    current = _found(await repository.get_by_id(user_id))
    if current.role is role:
        # Nothing to write, so the modification stamp is not moved: a request
        # that changes nothing must not look like an administrative action in
        # the only audit trail this screen has.
        return current

    updated = _found(await repository.update_role(user_id, role))
    logger.info(
        "usuario_rol_cambiado",
        user_id=str(updated.id),
        username=updated.username,
        rol_anterior=current.role.value,
        rol_nuevo=updated.role.value,
        actor=actor.username,
    )
    return updated


async def set_disabled(
    repository: AdminUserRepository,
    *,
    user_id: uuid.UUID,
    disabled: bool,
    actor: UserOut,
) -> UserAdminOut:
    """Disable or re-enable a user with a logical delete, never a physical one.

    Disabling an already disabled user succeeds and returns the same row: the
    operation is idempotent, which is what ``DELETE`` is supposed to be. The
    idempotence is real and not apparent -no write happens- so the second call
    answers with the modification stamp the first one left.

    Args:
        repository: Administration side of ``app_user``.
        user_id: Primary key of the user being disabled or re-enabled.
        disabled: Target value of the soft delete flag.
        actor: Administrator running the session.

    Returns:
        The user as it stands after the operation.

    Raises:
        HTTPException: 403 when the row of the caller no longer carries the
            administration role, whatever their token still claims; 404 when
            the user does not exist; 409 ``admin_no_puede_desactivarse`` when
            the actor disables their own row. Re-enabling one's own row is
            unreachable -a disabled actor cannot authenticate- and therefore is
            not special cased.
    """
    guard_actor_still_admin(actor)
    guard_self_disable(user_id, disabled, actor)

    current = _found(await repository.get_by_id(user_id))
    if current.disabled == disabled:
        return current

    updated = _found(await repository.set_disabled(user_id, disabled))
    logger.info(
        "usuario_desactivado" if disabled else "usuario_reactivado",
        user_id=str(updated.id),
        username=updated.username,
        rol_actual=updated.role.value,
        actor=actor.username,
    )
    return updated


async def apply_partial_update(
    repository: AdminUserRepository,
    *,
    user_id: uuid.UUID,
    change: UserRoleUpdate,
    actor: UserOut,
) -> UserAdminOut:
    """Apply a partial update: the role first, the access flag second.

    The role of the caller and both self protection rules are evaluated before
    the first read, so a body that would be rejected never reaches the database,
    and the 404 is decided once and up front, so a body carrying two changes
    over an unknown user cannot apply half of itself.

    Args:
        repository: Administration side of ``app_user``.
        user_id: Primary key of the user being changed.
        change: Validated body. Its model validator guarantees that at least
            one of the two fields is present.
        actor: Administrator running the session.

    Returns:
        The user as it stands after every requested change.

    Raises:
        HTTPException: 403 when the row of the caller no longer carries the
            administration role; 404 when the user does not exist; 409 when the
            actor targets their own row with a change the portal forbids.
    """
    guard_actor_still_admin(actor)
    if change.role is not None:
        guard_self_demotion(user_id, change.role, actor)
    if change.disabled is not None:
        guard_self_disable(user_id, change.disabled, actor)

    updated = _found(await repository.get_by_id(user_id))
    if change.role is not None:
        updated = await change_role(
            repository, user_id=user_id, role=change.role, actor=actor
        )
    if change.disabled is not None:
        updated = await set_disabled(
            repository, user_id=user_id, disabled=change.disabled, actor=actor
        )
    return updated


def guard_actor_still_admin(actor: UserOut) -> None:
    """Refuse any write from a caller the database no longer calls administrator.

    The permission of these endpoints is granted by the ``scope`` claim, which
    is written once when the session opens and never revised; the row can change
    underneath it at any moment. Without this check that gap is not a delay but
    a permanent hole: an administrator demoted at 10:05 still holds a token
    saying ``admin``, sends ``PATCH`` on their own row asking for ``admin``, and
    the demotion undoes itself. Reading the stored role costs nothing here:
    ``UserOut`` already carries it, because ``get_current_user`` had to load the
    row anyway in order to reject a deleted or a disabled account.

    The answer is 403 and not 409: what is missing is a permission of the
    caller, not a state of the target row. The code is the one
    ``app.core.scopes`` already publishes for a denied authorization, so a stale
    token is refused with the same body and the same challenge as a token that
    never carried the role, and the difference between the two is not
    observable from outside.

    Args:
        actor: Caller of the operation, described as the database has them now.

    Raises:
        HTTPException: 403 ``permisos_insuficientes``.
    """
    if actor.role is Scope.ADMIN:
        return
    logger.info(
        "usuario_escritura_denegada",
        codigo=ErrorCode.PERMISOS_INSUFICIENTES.value,
        actor=actor.username,
        rol_almacenado=actor.role.value,
    )
    raise forbidden([Scope.ADMIN.value])


def guard_self_demotion(user_id: uuid.UUID, role: Scope, actor: UserOut) -> None:
    """Refuse to take the administration role away from the caller.

    It runs before any repository call on purpose: a guard evaluated after the
    write demotes the administrator and only then reports the error.

    The exception carved out for the no-op rests on the role the database
    stores, never on the role the body asks for. Read from the body, a request
    that names the administration role over one's own row looks harmless by
    definition, and it is harmless only while the caller still is an
    administrator: for a demoted one that very same body is a promotion back to
    what was just taken away.

    Args:
        user_id: Primary key of the user being changed.
        role: Role the caller asked for.
        actor: Administrator running the session.

    Raises:
        HTTPException: 409 ``admin_no_puede_degradarse``.
    """
    if user_id != actor.id or (role is Scope.ADMIN and actor.role is Scope.ADMIN):
        return
    logger.info(
        "usuario_conflicto_autoproteccion",
        codigo=UserErrorCode.ADMIN_NO_PUEDE_DEGRADARSE.value,
        actor=actor.username,
        rol_nuevo=role.value,
    )
    raise _conflict(UserErrorCode.ADMIN_NO_PUEDE_DEGRADARSE)


def guard_self_disable(user_id: uuid.UUID, disabled: bool, actor: UserOut) -> None:
    """Refuse to cut the access of the caller.

    This rule, and not a count of administrators, is what keeps the portal from
    running out of them: reaching zero would require the last administrator to
    act on their own row, and no one else can act on it for them.

    Args:
        user_id: Primary key of the user being changed.
        disabled: Value of the flag the caller asked for.
        actor: Administrator running the session.

    Raises:
        HTTPException: 409 ``admin_no_puede_desactivarse``.
    """
    if not disabled or user_id != actor.id:
        return
    logger.info(
        "usuario_conflicto_autoproteccion",
        codigo=UserErrorCode.ADMIN_NO_PUEDE_DESACTIVARSE.value,
        actor=actor.username,
    )
    raise _conflict(UserErrorCode.ADMIN_NO_PUEDE_DESACTIVARSE)


def _found(user: UserAdminOut | None) -> UserAdminOut:
    """Narrow an optional row, turning the absent case into a 404.

    Args:
        user: Row returned by the repository, possibly absent.

    Returns:
        The row, once it is known to exist.

    Raises:
        HTTPException: 404 with the code ``usuario_no_encontrado``. The absence
            is reported and never serialised as a 200 with a null body.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserErrorCode.USUARIO_NO_ENCONTRADO.value,
        )
    return user


def _conflict(code: UserErrorCode) -> HTTPException:
    """Build the 409 of a self protection rule.

    It is 409 and not 403 on purpose: the administrator does hold the
    permission -``guard_actor_still_admin`` verified it against the row and not
    only against the token- and what clashes is the state of the resource, not
    the level of the caller.

    Args:
        code: Stable business code of the conflict.

    Returns:
        The exception to raise, carrying the code and nothing else.
    """
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=code.value)
