"""FastAPI security dependencies.

US-015 creates this module whole, scope enforcement included. US-016 consumes it
from the data routers and must not edit it: see ``docs/us-planning/us-015.md``
section 5.3. Hierarchy and vocabulary live in ``app.core.scopes``, owned by
US-016. This module neither declares nor compares them: it resolves the caller,
binds the identity to the log context and delegates the decision.
"""

from typing import Annotated, Final

import jwt
import structlog
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from app.core.scopes import (
    ErrorCode,
    enforce_scopes,
    oauth2_scope_descriptions,
    parse_scope_claim,
    unauthorized,
)
from app.core.security import decode_access_token
from app.models.user import UserOut
from app.services.user_service import UserRepository, get_user_repository

# auto_error=False is deliberate: with the default FastAPI answers its own 401,
# in English and without the stable code the frontend keys its copy on, and the
# "no token at all" case would fall outside the error contract of this US.
oauth2_scheme: Final[OAuth2PasswordBearer] = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token",
    scopes=oauth2_scope_descriptions(),
    auto_error=False,
)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserOut:
    """Resolve the caller and enforce the scopes the endpoint declared.

    Args:
        security_scopes: Scopes declared by the endpoint through ``Security``.
        token: Bearer token taken from the ``Authorization`` header, absent when
            the request carried no credentials.
        repository: Read side of ``app_user``.

    Returns:
        The identity of the caller, without the password digest.

    Raises:
        HTTPException: 401 with ``WWW-Authenticate`` when the token is absent,
            invalid, expired or points at a disabled user; 403 when the role in
            the token sits below the lowest scope the endpoint requires.
    """
    required = security_scopes.scopes

    if token is None:
        raise unauthorized(ErrorCode.CREDENCIALES_AUSENTES, required)

    try:
        claims = decode_access_token(token)
    except jwt.ExpiredSignatureError as error:
        raise unauthorized(ErrorCode.SESION_EXPIRADA, required) from error
    except jwt.InvalidTokenError as error:
        raise unauthorized(ErrorCode.CREDENCIALES_INVALIDAS, required) from error

    user = await repository.get_by_username(claims.username)
    if user is None:
        # A signature that verifies over a user that no longer exists is not a
        # valid session: the row is the source of truth, not the claim.
        raise unauthorized(ErrorCode.CREDENCIALES_INVALIDAS, required)
    if user.disabled:
        raise unauthorized(ErrorCode.SESION_REVOCADA, required)

    # Bound before enforcing so that the denial recorded by enforce_scopes
    # carries the identity without that function ever seeing the token.
    structlog.contextvars.bind_contextvars(usuario=user.username, rol=user.role)
    enforce_scopes(parse_scope_claim(claims.role), required)

    return UserOut.model_validate(user, from_attributes=True)
