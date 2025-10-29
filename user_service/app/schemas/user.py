"""Pydantic schemas for user creation, update, and response models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# -----------------------------
# Base
# -----------------------------
class UserBase(BaseModel):
    """Shared user fields."""
    email: EmailStr = Field(
        ...,
        json_schema_extra={"example": "user@example.com"},
    )
    full_name: Optional[str] = Field(
        None,
        json_schema_extra={"example": "John Doe"},
    )
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False
    is_superuser: Optional[bool] = False


# -----------------------------
# Create
# -----------------------------
class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(
        ...,
        min_length=8,
        json_schema_extra={"example": "StrongPassword123!"},
    )


# -----------------------------
# Update
# -----------------------------
class UserUpdate(BaseModel):
    """Schema for updating a user."""
    full_name: Optional[str] = Field(None)
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None


# -----------------------------
# Response
# -----------------------------
class UserOut(UserBase):  # pylint: disable=too-few-public-methods
    """Schema for returning user details."""
    id: UUID
    created_at: datetime
    updated_at: datetime
