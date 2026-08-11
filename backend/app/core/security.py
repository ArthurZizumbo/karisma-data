"""Cryptographic primitives of the portal: password hashing and access tokens.

This module owns the only ``PasswordHash`` instance of the project and the only
place where a JWT is signed or decoded. It never touches the database, so both
the FastAPI dependencies and the service layer can import it without a cycle.

The thirty minute lifetime is a module constant and not a setting on purpose: it
is an acceptance criterion of US-015, and an environment variable would let a
deployment contradict it without a single test noticing.
"""

import secrets
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Final

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from app.core.config import get_settings

ALGORITHM: Final[str] = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 30

_SECONDS_PER_MINUTE: Final[int] = 60

# The single hasher of the backend: pwdlib's recommendation is argon2id, so
# every stored digest starts with the $argon2id$ prefix. Building a second one
# anywhere else would let two sets of parameters coexist in the same database.
password_hash: Final[PasswordHash] = PasswordHash.recommended()


@dataclass(frozen=True)
class TokenClaims:
    """Claims this project puts in an access token.

    Attributes:
        username: Value of the ``sub`` claim, the login identifier of the user.
        role: Raw ``scope`` claim, a space delimited list of role names. It is
            parsed by ``app.core.scopes.parse_scope_claim``, never compared
            here: this module knows the format of a token, not the vocabulary.
        issued_at: Value of the ``iat`` claim, in epoch seconds.
        expires_at: Value of the ``exp`` claim, in epoch seconds.
    """

    username: str
    role: str
    issued_at: int
    expires_at: int


def hash_password(plain_password: str) -> str:
    """Hash a password with argon2id.

    Args:
        plain_password: Password as typed by the user.

    Returns:
        The encoded digest, prefixed with ``$argon2id$``.
    """
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a password against a stored digest.

    A digest the hasher does not recognize is reported as a failed credential
    and not as a server error: a row carrying a legacy or corrupted hash must
    end in the same neutral 401 as a wrong password, never in a stack trace
    that tells the caller the account exists.

    Args:
        plain_password: Password as typed by the user.
        hashed_password: Digest stored in ``app_user.hashed_password``.

    Returns:
        ``True`` when the password matches the digest.
    """
    try:
        return password_hash.verify(plain_password, hashed_password)
    except UnknownHashError:
        return False


def burn_verification_cycle(plain_password: str) -> None:
    """Verify against a fixed dummy hash so a missing user costs the same time.

    Args:
        plain_password: Password as typed by the user. The result is discarded:
            only the elapsed time matters.
    """
    verify_password(plain_password, _dummy_hash())


def create_access_token(username: str, role: str) -> str:
    """Sign an HS256 token whose exp is exactly 30 minutes after its iat.

    Args:
        username: Login identifier stored in the ``sub`` claim.
        role: Role name stored in the ``scope`` claim.

    Returns:
        The encoded token.
    """
    issued_at = int(time.time())
    claims = {
        "sub": username,
        "scope": role,
        "iat": issued_at,
        "exp": issued_at + ACCESS_TOKEN_EXPIRE_MINUTES * _SECONDS_PER_MINUTE,
    }
    return jwt.encode(claims, get_settings().jwt_secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenClaims:
    """Decode and validate a token.

    The list of accepted algorithms is explicit, which is what closes the
    ``alg=none`` forgery, and the three claims the portal depends on are
    required: a token without ``scope`` is rejected instead of being read as a
    session with zero permissions.

    Args:
        token: Encoded token taken from the ``Authorization`` header.

    Returns:
        The claims carried by the token.

    Raises:
        jwt.ExpiredSignatureError: If ``exp`` is in the past.
        jwt.InvalidTokenError: If the signature or the format fail, or if a
            required claim is absent.
    """
    payload = jwt.decode(
        token,
        get_settings().jwt_secret_key,
        algorithms=[ALGORITHM],
        options={"require": ["exp", "sub", "scope"]},
    )
    return TokenClaims(
        username=str(payload["sub"]),
        role=str(payload["scope"]),
        issued_at=int(payload.get("iat", 0)),
        expires_at=int(payload["exp"]),
    )


@lru_cache(maxsize=1)
def _dummy_hash() -> str:
    """Return the digest of a random value, computed once per process.

    Returns:
        An argon2id digest nobody knows the input of, so that verifying against
        it can never succeed by accident.
    """
    return hash_password(secrets.token_urlsafe(32))
