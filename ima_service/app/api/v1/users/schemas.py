# FILE: ima_service/app/api/v1/users/schemas.py
"""Pydantic schemas for Users (shared enums; minimal & typed)."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from ima_service.app.domain.users.enums import UserGender, UserRole

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.]{3,32}$")


def validate_username(v: Optional[str]) -> Optional[str]:
    """Validate optional username against a strict pattern; return normalized value."""
    if not v:
        return None
    if not _USERNAME_RE.match(v):
        raise ValueError(
            "username must be 3–32 chars; letters, numbers, underscores, dots only"
        )
    return v


class UserBase(BaseModel):
    """Common user fields shared by read models and some payloads."""

    email: EmailStr
    username: Optional[str] = Field(default=None, max_length=32)
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_superuser: bool = False

    # Profile
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    gender: UserGender = UserGender.UNSPECIFIED

    @field_validator("username")
    @classmethod
    def _check_username(cls, v: Optional[str]) -> Optional[str]:
        return validate_username(v)


class UserCreate(BaseModel):
    """Payload to create a new user (email immutable after create)."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=1024)
    username: Optional[str] = Field(default=None, max_length=32)
    role: UserRole = UserRole.USER

    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    gender: UserGender = UserGender.UNSPECIFIED

    @field_validator("username")
    @classmethod
    def _check_username(cls, v: Optional[str]) -> Optional[str]:
        return validate_username(v)


class UserLogin(BaseModel):
    """Login payload."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=1024)


class UserUpdate(BaseModel):
    """Partial update for a user (email not updatable)."""

    username: Optional[str] = Field(default=None, max_length=32)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8, max_length=1024)

    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    gender: Optional[UserGender] = None

    @field_validator("username")
    @classmethod
    def _check_username(cls, v: Optional[str]) -> Optional[str]:
        return validate_username(v)


class UserRead(UserBase):
    """User representation returned by API endpoints."""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic configuration and example payload for documentation."""

        json_schema_extra = {
            "example": {
                "id": "7a0f8e0a-6b2e-4b93-9125-22e2f9a5af0e",
                "email": "alice@example.com",
                "username": "alice",
                "first_name": "Alice",
                "last_name": "Ng",
                "gender": "UNSPECIFIED",
                "role": "USER",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2025-09-19T10:00:00Z",
                "updated_at": "2025-09-19T10:00:00Z",
            }
        }
