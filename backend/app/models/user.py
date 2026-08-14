"""Persistence and response contracts of the portal users.

The four role literals are NOT declared here. ``Scope``, in ``app.core.scopes``,
is the single vocabulary of the backend: a second enumeration in this module is
exactly the divergence that section 5.5 of the US-015 plan resolved against.
"""

import uuid
from collections.abc import Mapping
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType
from typing import Final, Literal, Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from sqlmodel import Field, SQLModel

from app.core.scopes import Scope


class AppUser(SQLModel, table=True):
    """Mirror of the ``app_user`` table created by dbmate. It never creates schema.

    ``role`` is typed as ``str`` and not as ``Scope`` on purpose. With the
    enumeration here SQLAlchemy would map the column to its native ``Enum``
    type, and the real column is ``TEXT`` with a ``CHECK``, which is what lets a
    role be added without an ``ALTER TYPE``. The model mirrors the database; the
    response contract below validates the vocabulary.

    Attributes:
        id: Primary key, ``gen_random_uuid()`` on the database side.
        username: Login identifier and ``sub`` claim of the token. Unique.
        email: Contact address. Unique.
        full_name: Name shown by the interface after signing in.
        hashed_password: argon2id digest. Never serialized out.
        role: One of the values of ``Scope``, enforced by a ``CHECK``.
        disabled: Soft delete flag. A disabled user never gets a session.
        created_at: Row creation timestamp, ``now()`` on the database side.
        updated_at: Last administrative change -role, disable or re-enable-,
            written explicitly by the administration repository. Optional
            because the column arrived with US-018 and the model is a mirror
            of the table, not its author.
    """

    __tablename__ = "app_user"

    id: uuid.UUID | None = Field(default=None, primary_key=True)
    username: str
    email: str
    full_name: str
    hashed_password: str
    role: str
    disabled: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserOut(SQLModel):
    """Response contract of a user. Deliberately without ``hashed_password``.

    Attributes:
        id: Primary key of the row.
        username: Login identifier.
        email: Contact address.
        full_name: Name shown by the interface.
        role: Role of the user, validated against the canonical vocabulary.
        disabled: Soft delete flag.
        created_at: Row creation timestamp.
    """

    id: uuid.UUID
    username: str
    email: str
    full_name: str
    role: Scope
    disabled: bool
    created_at: datetime


class Token(SQLModel):
    """Access token as OAuth 2.0 describes it.

    Attributes:
        access_token: Encoded JWT.
        token_type: Always ``bearer``; the value is the OAuth 2.0 token type
            and not a credential, despite what the secret linter reads in the
            field name.
    """

    access_token: str
    token_type: Literal["bearer"] = "bearer"  # noqa: S105


class TokenDemostracion(Token):
    """Token of the demo access, labelled as what it is.

    It lives next to ``Token`` and not in the router because the service layer
    returns it, and a service that imported the API layer would invert the
    dependency the project is built on.

    Attributes:
        modo: Fixed ``demostracion`` marker, so no client can mistake a
            credential-free session for a real one.
    """

    modo: Literal["demostracion"] = "demostracion"


class UserErrorCode(StrEnum):
    """Stable business codes returned in ``detail`` by the users API.

    They are not authorization codes: ``ErrorCode`` in ``app.core.scopes``
    answers who you are and what you may do, while these answer what happened to
    this row. Keeping the two vocabularies apart is why this US never edits
    ``app/core/scopes.py``.
    """

    USUARIO_NO_ENCONTRADO = "usuario_no_encontrado"
    ADMIN_NO_PUEDE_DEGRADARSE = "admin_no_puede_degradarse"
    ADMIN_NO_PUEDE_DESACTIVARSE = "admin_no_puede_desactivarse"
    SIN_CAMBIOS_SOLICITADOS = "sin_cambios_solicitados"


# Spelling the interface once used for the administration role and the database
# CHECK rejects. A client still sending it gets a message naming the canonical
# literal instead of the opaque enum error Pydantic would emit on its own.
_ROLE_MISSPELLINGS: Final[Mapping[str, Scope]] = MappingProxyType(
    {"administrador": Scope.ADMIN}
)


class UserAdminOut(UserOut):
    """Response contract of the administration endpoints.

    It extends ``UserOut`` instead of replacing it so that the ``/api/auth/me``
    contract frozen by US-015 keeps its exact shape. Like its parent, it
    deliberately has no ``hashed_password`` field, and the absence is a property
    rather than a promise: the administration repository never selects that
    column, so nothing upstream of here can carry it.

    Attributes:
        updated_at: Timestamp of the last administrative change of the row.
    """

    updated_at: datetime


class UserPage(SQLModel):
    """One page of the user list. Shaped as an object, never as a bare array.

    Turning an array response into an object later is a breaking change for the
    client, and it costs nothing to decide today.

    Attributes:
        items: Users of this page, ordered by ``username`` ascending.
        total: Users in the table, not in the page.
        limit: Page size the caller asked for.
        offset: Rows skipped before the page.
    """

    items: list[UserAdminOut]
    total: int
    limit: int
    offset: int


class UserRoleUpdate(BaseModel):
    """Body of ``PATCH /api/users/{user_id}``. Every field optional, one required.

    ``extra="forbid"`` is not ceremony: it is what makes a client that sends
    ``{"username": "otro"}`` -believing the full edition that the S4 scope cut
    removed still exists- receive an explicit 422 instead of a silent 200 that
    changed nothing.

    Attributes:
        role: New role of the user, or ``None`` to leave it as it is.
        disabled: New soft delete flag, or ``None`` to leave it as it is.
    """

    model_config = ConfigDict(extra="forbid")

    role: Scope | None = None
    disabled: bool | None = None

    @field_validator("role", mode="before")
    @classmethod
    def reject_known_misspellings(cls, value: object) -> object:
        """Turn the known wrong spelling of the admin role into a readable 422.

        ``administrador`` is the spelling US-015 forbids and US-017 erased from
        the interface. A client that still sends it deserves a message naming
        the canonical literal instead of an opaque enum error.

        Args:
            value: Raw value of the ``role`` field, before coercion.

        Returns:
            The value untouched when it is not a known misspelling.

        Raises:
            ValueError: When the value is a spelling the portal deliberately
                dropped.
        """
        if isinstance(value, str):
            canonical = _ROLE_MISSPELLINGS.get(value)
            if canonical is not None:
                message = (
                    f"'{value}' no es un rol del portal; el literal canonico es "
                    f"'{canonical.value}'"
                )
                raise ValueError(message)
        return value

    @model_validator(mode="after")
    def at_least_one_change(self) -> Self:
        """Reject an empty body with 422 and the ``SIN_CAMBIOS_SOLICITADOS`` code.

        Returns:
            The validated body.

        Raises:
            ValueError: When neither field was sent, which is a request that
                would answer 200 without changing anything.
        """
        if self.role is None and self.disabled is None:
            message = (
                f"{UserErrorCode.SIN_CAMBIOS_SOLICITADOS.value}: envia al menos "
                "uno de 'role' o 'disabled'"
            )
            raise ValueError(message)
        return self
