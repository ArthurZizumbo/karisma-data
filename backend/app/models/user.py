"""Persistence and response contracts of the portal users.

The four role literals are NOT declared here. ``Scope``, in ``app.core.scopes``,
is the single vocabulary of the backend: a second enumeration in this module is
exactly the divergence that section 5.5 of the US-015 plan resolved against.
"""

import uuid
from datetime import datetime
from typing import Literal

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
