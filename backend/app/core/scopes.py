"""Role vocabulary and authorization primitives of Karisma Data.

This module is the only place where the four roles of the portal are named and
ordered. It knows nothing about routing, persistence or token format: it answers
one question -does this principal reach the level an endpoint demands- and builds
the two RFC 6750 challenges the API is allowed to return. Keeping it free of
imports from ``app.api``, ``app.models`` and ``app.core.config`` is what lets the
permission matrix run without a database and without the authentication module.

Ownership: the declared owner of this file is US-016. US-015 creates it ahead of
time, implementing exactly the public surface US-016 froze in
``docs/us-planning/us-016.md`` section 4.1, because ``app.core.auth`` cannot
enforce scopes without it and US-015 is forbidden from opening a second role
vocabulary (section 5.5, resolutions 1 and 2 of ``docs/us-planning/us-015.md``).
US-016 adds ``app/core/permissions.py`` on top and owns every later change here.
"""

from collections.abc import Collection, Mapping
from enum import StrEnum
from types import MappingProxyType
from typing import Final, Protocol

import structlog
from fastapi import HTTPException, status

logger = structlog.get_logger()

# Protection space of RFC 7235. One realm for the whole API: every challenge the
# portal emits names it, so a client can tell our 401 from a proxy's.
REALM: Final[str] = "karisma"


class Scope(StrEnum):
    """Role granted by the access token. Canonical vocabulary of the portal."""

    OPERATIVO = "operativo"
    ANALISTA = "analista"
    DIRECTIVO = "directivo"
    ADMIN = "admin"


class ErrorCode(StrEnum):
    """Stable error codes returned in the ``detail`` field.

    They are contract, not prose: the interface is bilingual, so the Spanish and
    English copy lives in the frontend locales and never in the response body.
    """

    CREDENCIALES_AUSENTES = "credenciales_ausentes"
    CREDENCIALES_INVALIDAS = "credenciales_invalidas"
    SESION_EXPIRADA = "sesion_expirada"
    SESION_REVOCADA = "sesion_revocada"
    PERMISOS_INSUFICIENTES = "permisos_insuficientes"


# Total order. 'admin' covers every level by design; the separation of duties
# limitation this implies is recorded in docs/security.md section 11.
ROLE_HIERARCHY: Final[Mapping[Scope, int]] = MappingProxyType(
    {
        Scope.OPERATIVO: 0,
        Scope.ANALISTA: 1,
        Scope.DIRECTIVO: 2,
        Scope.ADMIN: 3,
    }
)

# Codes whose reason is safe to publish in the challenge: both tell the client
# that retrying with the same token is pointless, and neither reveals whether
# the account exists.
_DESCRIBED_CODES: Final[frozenset[ErrorCode]] = frozenset(
    {ErrorCode.SESION_EXPIRADA, ErrorCode.SESION_REVOCADA}
)

_SCOPE_VALUES: Final[frozenset[str]] = frozenset(scope.value for scope in Scope)

# Shown by the Authorize button of Swagger, which is how every endpoint of the
# portal is probed by hand.
_SCOPE_DESCRIPTIONS: Final[Mapping[Scope, str]] = MappingProxyType(
    {
        Scope.OPERATIVO: "Consulta puntual de datos y catalogo",
        Scope.ANALISTA: "Agregaciones, exploracion y exportaciones",
        Scope.DIRECTIVO: "Resumenes ejecutivos y tableros directivos",
        Scope.ADMIN: "Administracion de usuarios y de la plataforma",
    }
)


class Principal(Protocol):
    """Minimum shape the authentication layer must supply to authorize."""

    username: str
    role: Scope
    disabled: bool


def parse_scope_claim(raw: str) -> frozenset[Scope]:
    """Parse the space delimited ``scope`` claim, dropping unknown names.

    A name the portal does not know is not an error: it is a permission that
    grants nothing. Raising here would turn an old or forged token into a 500.

    Args:
        raw: Value of the ``scope`` claim, one or more names separated by
            whitespace.

    Returns:
        The set of roles the token actually grants.
    """
    return frozenset(Scope(name) for name in raw.split() if name in _SCOPE_VALUES)


def covers(granted: Collection[Scope], required: Collection[str]) -> bool:
    """Report whether the granted roles reach every required scope.

    The function fails closed on both sides. A required name outside the
    vocabulary means the endpoint is misdeclared, and a misdeclared endpoint
    denies instead of crashing; an empty set of granted roles means the token
    carried nothing this portal understands.

    Args:
        granted: Roles carried by the access token.
        required: Scope names the endpoint declared, possibly empty.

    Returns:
        ``True`` when access is allowed, ``False`` otherwise.
    """
    if not required:
        return True

    unknown = sorted({name for name in required if name not in _SCOPE_VALUES})
    if unknown:
        logger.warning("scope_desconocido", scopes_exigidos=unknown)
        return False

    if not granted:
        return False

    highest_granted = max(ROLE_HIERARCHY[scope] for scope in granted)
    highest_required = max(ROLE_HIERARCHY[Scope(name)] for name in required)
    return highest_granted >= highest_required


def enforce_scopes(granted: Collection[Scope], required: Collection[str]) -> None:
    """Raise 403 when the granted roles do not reach the required level.

    Args:
        granted: Roles carried by the access token.
        required: Scope names the endpoint declared, possibly empty.

    Raises:
        HTTPException: 403 with the ``insufficient_scope`` challenge.
    """
    if covers(granted, required):
        return

    # Neither the token nor the identity is logged here: the username arrives
    # through structlog.contextvars, bound by app.core.auth once the session is
    # resolved, and main.py merges it into every record.
    logger.info(
        "autorizacion_denegada",
        scopes_exigidos=sorted(required),
        scopes_del_token=sorted(scope.value for scope in granted),
    )
    raise forbidden(required)


def unauthorized(code: ErrorCode, required: Collection[str] = ()) -> HTTPException:
    """Build the 401 challenge for the given failure code.

    Args:
        code: Stable reason of the failure, returned as ``detail``.
        required: Scope names the endpoint declared, echoed in the challenge so
            a conforming client knows what to ask for.

    Returns:
        The exception to raise, with its ``WWW-Authenticate`` header.
    """
    # The two RFC 6750 error values are written inline, and not as module
    # constants, because a constant whose name ends in _TOKEN reads as a
    # hardcoded credential to the secret linter and would need a blanket noqa.
    error = None if code is ErrorCode.CREDENCIALES_AUSENTES else "invalid_token"
    description = code if code in _DESCRIBED_CODES else None
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=code.value,
        headers={"WWW-Authenticate": _challenge(error, description, required)},
    )


def forbidden(required: Collection[str]) -> HTTPException:
    """Build the 403 ``insufficient_scope`` challenge.

    The body carries the code and nothing else: no resource name, no owner, no
    hint beyond the level the challenge already implies.

    Args:
        required: Scope names the endpoint declared.

    Returns:
        The exception to raise, with its ``WWW-Authenticate`` header.
    """
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=ErrorCode.PERMISOS_INSUFICIENTES.value,
        headers={"WWW-Authenticate": _challenge("insufficient_scope", None, required)},
    )


def oauth2_scope_descriptions() -> dict[str, str]:
    """Return the scope catalogue consumed by ``OAuth2PasswordBearer``.

    Returns:
        A fresh mapping of scope name to its human description, so that FastAPI
        cannot mutate the module level catalogue.
    """
    return {scope.value: text for scope, text in _SCOPE_DESCRIPTIONS.items()}


def _challenge(
    error: str | None, description: ErrorCode | None, required: Collection[str]
) -> str:
    """Assemble a ``WWW-Authenticate`` value following RFC 6750 section 3.

    Args:
        error: Value of the ``error`` parameter, omitted when the request
            carried no credentials at all.
        description: Code published as ``error_description``, when the reason is
            safe to disclose.
        required: Scope names echoed as the ``scope`` parameter.

    Returns:
        The header value, always starting with the ``Bearer`` scheme.
    """
    parameters = [f'realm="{REALM}"']
    if error is not None:
        parameters.append(f'error="{error}"')
    if description is not None:
        parameters.append(f'error_description="{description.value}"')
    if required:
        parameters.append(f'scope="{" ".join(required)}"')
    return f"Bearer {', '.join(parameters)}"
