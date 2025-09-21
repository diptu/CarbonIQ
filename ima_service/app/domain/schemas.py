"""Pydantic I/O schemas (users only)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field
from typing_extensions import Annotated

from app.domain.models import UserRole

ShortName = Annotated[str, Field(min_length=1, max_length=80, strip_whitespace=True)]
Password = Annotated[str, Field(min_length=8, max_length=128)]


class UserCreate(BaseModel):
    """Create User Schema"""

    email: EmailStr
    name: ShortName
    password: Password
    role: UserRole = UserRole.VIEWER


class UserRead(BaseModel):
    """Get User Schema"""

    id: UUID
    email: EmailStr
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime


class UserFilter(BaseModel):
    """Search User Schema"""

    role: UserRole | None = None
    active_only: bool = True


class TokenPair(BaseModel):
    """Token Obtain Schema"""

    access: str
    refresh: str
