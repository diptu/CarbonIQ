"""Authentication token schemas for the RBAC system."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .base import ORMBaseSchema


class AuthTokenBase(BaseModel):
    """Base schema for authentication tokens.

    Notes
    -----
    - Shared fields for token models.
    - Represents refresh/session tokens tied to users.
    """

    user_id: uuid.UUID = Field(..., description="Associated user ID")
    token: str = Field(..., description="Opaque refresh or session token")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    revoked: bool = Field(default=False, description="Whether token is revoked")


class AuthTokenCreate(AuthTokenBase):
    """Schema for creating a new authentication token.

    Parameters
    ----------
    user_id : UUID
        Identifier of the user who owns the token.
    token : str
        Raw refresh token string (to be hashed in storage).
    expires_at : datetime
        Time when the token expires.
    revoked : bool, default False
        Indicates whether the token is revoked.
    """

    @field_validator("token")
    @classmethod
    def validate_token(cls, value: str) -> str:
        """Ensure token is not empty."""
        if not value.strip():
            raise ValueError("Token string cannot be empty.")
        return value


class AuthTokenUpdate(BaseModel):
    """Schema for updating an existing auth token (PATCH semantics)."""

    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    revoked: Optional[bool] = None


class AuthTokenRead(AuthTokenBase, ORMBaseSchema):
    """Schema for reading token data."""

    id: uuid.UUID = Field(..., description="Unique token identifier")


class AuthTokenInDB(AuthTokenRead):
    """Internal schema for DB-level token representation.

    Notes
    -----
    - Includes relationship data (user info) when necessary.
    """

    user_email: Optional[str] = Field(
        None, description="Email of linked user (optional join)"
    )


__all__ = [
    "AuthTokenBase",
    "AuthTokenCreate",
    "AuthTokenUpdate",
    "AuthTokenRead",
    "AuthTokenInDB",
]
