"""Pydantic schemas for user creation, update, and response models with enhanced structure."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# -----------------------------
# Base schema
# -----------------------------
class UserBase(BaseModel):
    """Shared user fields."""

    email: EmailStr = Field(
        ..., json_schema_extra={"example": "user@example.com"}, description="User email address"
    )
    full_name: Optional[str] = Field(
        None, json_schema_extra={"example": "John Doe"}, description="Full name of the user"
    )
    is_active: bool = Field(True, description="Indicates if the user is active")
    is_verified: bool = Field(False, description="Indicates if the user has verified their email")
    is_superuser: bool = Field(False, description="Indicates if the user is a superuser/admin")


# -----------------------------
# Create schema
# -----------------------------
class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(
        ...,
        min_length=8,
        json_schema_extra={"example": "StrongPassword123!"},
        description="Password for the user account",
    )


# -----------------------------
# Update schema
# -----------------------------
class UserUpdate(BaseModel):
    """Schema for updating an existing user."""

    full_name: Optional[str] = Field(None, description="Updated full name of the user")
    is_active: Optional[bool] = Field(None, description="Update active status")
    is_verified: Optional[bool] = Field(None, description="Update verification status")
    is_superuser: Optional[bool] = Field(None, description="Update superuser/admin status")


# -----------------------------
# Response schema
# -----------------------------
class UserOut(UserBase):
    """Schema for returning user details, including timestamps and ID."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)  # Enable ORM parsing
