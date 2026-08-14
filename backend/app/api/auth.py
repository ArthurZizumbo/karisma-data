"""Authentication endpoints. They receive, delegate and answer: no logic here.

Two of the three routes are public by design and both are declared in the
whitelist of US-016: ``POST /api/auth/token``, which cannot demand a token in
order to emit one, and ``POST /api/auth/demo``, which additionally exists only
while ``DEMO_LOGIN_ENABLED`` is on. ``GET /api/auth/me`` is the only endpoint of
this US behind ``Security``, and it declares no scope: any valid session may
read its own identity.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, Security, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.core.scopes import ErrorCode, Scope
from app.models.user import Token, TokenDemostracion, UserOut
from app.services.auth_service import (
    CREDENCIALES_INVALIDAS,
    demo_login,
    login,
)
from app.services.user_service import UserRepository, get_user_repository

router = APIRouter(prefix="/api/auth", tags=["autenticacion"])

# Public by design, and only mounted when DEMO_LOGIN_ENABLED is true. US-016
# registers RouteKey("POST", "/api/auth/demo") in PUBLIC_ROUTES so that its
# startup guard accepts the route.
demo_router = APIRouter(prefix="/api/auth", tags=["autenticacion"])


class DemoLoginRequest(BaseModel):
    """Body of the demo access. An unknown role yields 422, never a 500.

    Attributes:
        rol: Role whose canonical demo user is requested.
    """

    rol: Scope = Field(description="Rol del usuario canonico de demostracion")


@router.post("/token", response_model=Token, summary="Emite un token de acceso")
async def create_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> Token:
    """Exchange a username and a password for an access token.

    Args:
        form: Standard OAuth 2.0 password form, sent as form-urlencoded.
        repository: Read side of ``app_user``.

    Returns:
        The signed access token.
    """
    return await login(repository, form.username, form.password)


@router.get("/me", response_model=UserOut, summary="Sesion del usuario actual")
async def read_me(
    current_user: Annotated[UserOut, Security(get_current_user)],
) -> UserOut:
    """Return the identity behind the token of the request.

    Args:
        current_user: Caller resolved by the security dependency.

    Returns:
        The identity of the caller, without the password digest.
    """
    return current_user


@demo_router.post(
    "/demo",
    response_model=TokenDemostracion,
    summary="Acceso de demostracion, sin credenciales, solo en el prototipo",
)
async def create_demo_token(
    body: DemoLoginRequest,
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> TokenDemostracion:
    """Emit a token for the canonical demo user of a role, with no password.

    Args:
        body: Requested role.
        repository: Read side of ``app_user``.

    Returns:
        The signed access token, labelled as a demonstration.
    """
    return await demo_login(repository, body.rol)


async def handle_invalid_credentials(
    _request: Request, _error: Exception
) -> JSONResponse:
    """Render the neutral 401 of the authentication endpoints.

    FastAPI serializes ``HTTPException`` as ``{"detail": ...}`` and nothing
    else, and the contract of this US also carries a stable ``codigo`` next to
    the Spanish literal, because the interface is bilingual and keys its copy on
    the code. The body is built from the module constants and not from the
    exception instance: Starlette types every handler against the base
    ``Exception``, and the exception deliberately carries no data.

    Args:
        _request: Unused; the handler answers the same for every request.
        _error: Unused; the type of the exception is the whole information.

    Returns:
        The 401 with the neutral message, its stable code and the challenge.
    """
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "detail": CREDENCIALES_INVALIDAS,
            "codigo": ErrorCode.CREDENCIALES_INVALIDAS.value,
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
