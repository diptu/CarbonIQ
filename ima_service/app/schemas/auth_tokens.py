"""Pydantic schemas for authentication tokens.

Includes base, create, update, read, and internal DB schemas
for multi-tenant token management with validation.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Literal, Dict

from pydantic import BaseModel, Field, field_validator, model_validator

from .base import ORMBaseSchema


class AuthTokenBase(BaseModel):
    """Base schema for authentication tokens."""

    user_id: uuid.UUID = Field(..., description="Associated user ID")
    token: str = Field(..., description="Opaque refresh or session token")
    jti: str = Field(..., description="JWT ID for session correlation")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    revoked: bool = Field(default=False, description="Whether token is revoked")
    revoked_at: Optional[datetime] = Field(None, description="Timestamp when revoked")
    device_info: Optional[str] = Field(None, description="Device or client info")
    ip_address: Optional[str] = Field(None, description="IP address of request origin")

    # Use timezone.utc for default factory for consistency
    issued_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Token issuance timestamp"
    )
    last_used_at: Optional[datetime] = Field(None, description="Last time token was used")
    session_type: Optional[str] = Field(None, description="Optional session type")
    token_type: Literal["access", "refresh", "api_key"] = Field(
        "access", description="Type of token"
    )
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    trace_id: Optional[str] = Field(None, description="Distributed trace ID")
    extra: Optional[Dict] = Field(default_factory=dict, description="Flexible JSON metadata")
    mfa_verified: Optional[bool] = Field(None, description="Whether MFA was verified")
    tenant_id: Optional[uuid.UUID] = Field(
        None, description="Tenant context for multi-tenant reporting"
    )

    @field_validator("token")
    @classmethod
    def validate_token(cls, value: str) -> str:
        """Ensure token string is not empty."""
        if not value.strip():
            raise ValueError("Token string cannot be empty.")
        return value

    @field_validator("jti")
    @classmethod
    def validate_jti(cls, value: str) -> str:
        """Ensure JWT ID is not empty."""
        if not value.strip():
            raise ValueError("JWT ID (jti) cannot be empty.")
        return value

    @model_validator(mode="before")
    @classmethod
    def validate_expiry(cls, values):
        """Validate that expires_at is later than issued_at."""
        issued = values.get("issued_at")
        expires = values.get("expires_at")
        if issued and expires and expires <= issued:
            raise ValueError("expires_at must be later than issued_at")
        return values


class AuthTokenCreate(AuthTokenBase):
    """Schema for creating a new authentication token."""


class AuthTokenUpdate(BaseModel):
    """Schema for updating an existing authentication token."""

    token: Optional[str] = None
    jti: Optional[str] = None
    expires_at: Optional[datetime] = None
    revoked: Optional[bool] = None
    revoked_at: Optional[datetime] = None
    device_info: Optional[str] = None
    ip_address: Optional[str] = None
    last_used_at: Optional[datetime] = None
    session_type: Optional[str] = None
    token_type: Optional[Literal["access", "refresh", "api_key"]] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    extra: Optional[Dict] = None
    mfa_verified: Optional[bool] = None

    # 🔑 NEW: Apply validation logic from AuthTokenBase
    _validate_token = field_validator("token", mode="before")(AuthTokenBase.validate_token)
    _validate_jti = field_validator("jti", mode="before")(AuthTokenBase.validate_jti)
    _validate_expiry = model_validator(mode="before")(AuthTokenBase.validate_expiry)


class AuthTokenRead(AuthTokenBase, ORMBaseSchema):
    """Schema for reading token data with ID and full audit fields."""

    id: uuid.UUID = Field(..., description="Unique token identifier")


class AuthTokenInDB(AuthTokenRead):
    """Internal schema including optional user email join for reporting."""

    user_email: Optional[str] = Field(None, description="Email of linked user (optional join)")
    # Note: user_id and tenant_id are present via AuthTokenRead/ORMBaseSchema


__all__ = [
    "AuthTokenBase",
    "AuthTokenCreate",
    "AuthTokenUpdate",
    "AuthTokenRead",
    "AuthTokenInDB",
]
