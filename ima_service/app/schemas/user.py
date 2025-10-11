"""User schemas for multi-tenant RBAC system."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from .base import ORMBaseSchema


class UserBase(BaseModel):
    """Base schema with shared attributes.

    Notes
    -----
    - Represents fields shared by all user-related schemas.
    - Used internally to avoid duplication.
    """

    email: EmailStr = Field(..., max_length=255, description="User email")
    full_name: Optional[str] = Field(
        None, max_length=255, description="Full display name"
    )
    is_active: bool = Field(default=True, description="Indicates if user is active")
    tenant_id: Optional[uuid.UUID] = Field(
        None, description="Tenant this user belongs to"
    )


class UserCreate(UserBase):
    """Schema for user creation."""

    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        """Ensure password meets basic security requirements."""
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        return value


class UserUpdate(BaseModel):
    """Schema for updating existing users (PATCH semantics)."""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    tenant_id: Optional[uuid.UUID] = None


class UserRead(UserBase, ORMBaseSchema):
    """Schema for reading user information."""

    id: uuid.UUID = Field(..., description="Unique user identifier")


class UserInDB(UserRead):
    """Internal schema including password hash."""

    password_hash: str = Field(..., description="BCrypt hashed password")


__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserRead",
    "UserInDB",
]
