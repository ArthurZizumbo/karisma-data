"""Authentication of the portal: password flow and credential-free demo access.

Two rules govern this module. Every failure looks the same from the outside -one
status, one body, one header- so that response time and wording never tell an
attacker whether an account exists. And nothing that identifies a credential
reaches the log: no password, no token, and no username typed by whoever failed
to sign in, because people type their password in the user field more often than
it seems.
"""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

import structlog
from fastapi import HTTPException, status

from app.core import security
from app.core.scopes import Scope
from app.models.user import AppUser, Token, TokenDemostracion
from app.services.user_service import UserRepository

logger = structlog.get_logger()

# Canonical user of each role, used by the credential-free demo access. They are
# the first user seeded for each profile by the create_app_user migration.
DEMO_USERNAME_BY_ROLE: Final[Mapping[Scope, str]] = MappingProxyType(
    {
        Scope.OPERATIVO: "lmendez",
        Scope.ANALISTA: "dhernandez",
        Scope.DIRECTIVO: "acastaneda",
        Scope.ADMIN: "movalle",
    }
)

# Literal required by US-015. The interface never paints it: it is bilingual and
# renders its own i18n key from the 401, so this text is for the log, for
# Swagger and for whoever reads the API by hand.
CREDENCIALES_INVALIDAS: Final[str] = "Credenciales incorrectas"


class InvalidCredentialsError(HTTPException):
    """Neutral 401 of the authentication endpoints.

    Carries no data: the three ways of failing -unknown user, wrong password,
    disabled account- must produce the same response byte for byte, so the body
    is built from module constants by the handler in ``app.api.auth``.
    """

    def __init__(self) -> None:
        """Build the 401 with the neutral message and the bearer challenge."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=CREDENCIALES_INVALIDAS,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def authenticate_user(
    repository: UserRepository, username: str, password: str
) -> AppUser | None:
    """Return the user when the credentials match, ``None`` otherwise.

    A missing user still burns one verification cycle, so the response time
    never tells an attacker whether the username exists.

    Args:
        repository: Read side of ``app_user``.
        username: Login identifier, as typed by the caller.
        password: Password, as typed by the caller.

    Returns:
        The authenticated user, or ``None`` on any failure.
    """
    user = await repository.get_by_username(username)
    if user is None:
        security.burn_verification_cycle(password)
        return None
    if not security.verify_password(password, user.hashed_password):
        return None
    if user.disabled:
        return None
    return user


async def login(repository: UserRepository, username: str, password: str) -> Token:
    """Authenticate a user and mint an access token.

    Args:
        repository: Read side of ``app_user``.
        username: Login identifier, as typed by the caller.
        password: Password, as typed by the caller.

    Returns:
        The signed access token.

    Raises:
        InvalidCredentialsError: 401 with the neutral message on any failure.
    """
    user = await authenticate_user(repository, username, password)
    if user is None:
        # Deliberately without the username: a failed attempt is exactly where
        # a mistyped password ends up, and the log is not the place for it.
        logger.info("acceso_denegado", via="contrasena")
        raise InvalidCredentialsError

    logger.info("acceso_concedido", usuario=user.username, rol=user.role)
    return Token(access_token=security.create_access_token(user.username, user.role))


async def demo_login(repository: UserRepository, role: Scope) -> TokenDemostracion:
    """Mint a token for the canonical demo user of a role, with no password.

    The role argument only *selects* the canonical user. The scope claim is
    built from the role stored in that user's ``app_user`` row, so the demo
    token can never carry more than the seeded user already has, and a disabled
    canonical user raises 401 instead of yielding a token.

    Args:
        repository: Read side of ``app_user``.
        role: Role whose canonical user is requested.

    Returns:
        The signed access token, labelled as a demonstration.

    Raises:
        InvalidCredentialsError: 401 when the canonical user is absent from the
            database or disabled.
    """
    username = DEMO_USERNAME_BY_ROLE[role]
    user = await repository.get_by_username(username)
    if user is None or user.disabled:
        # The username here is seeded data, not something a visitor typed, and
        # naming it is the only way to see that the migration did not run.
        logger.warning("demostracion_no_disponible", usuario=username, rol=role.value)
        raise InvalidCredentialsError

    logger.info("acceso_concedido", usuario=user.username, rol=user.role, modo="demo")
    return TokenDemostracion(
        access_token=security.create_access_token(user.username, user.role)
    )
