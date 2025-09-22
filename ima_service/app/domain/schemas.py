"""Domain-level DTOs (independent of API/persistence)."""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    Owner = "owner"
    Editor = "editor"
    VIEWER = "viewer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: UserRole = Field(default=UserRole.VIEWER)


class User(BaseModel):
    id: str
    email: Optional[EmailStr] = None
    role: UserRole


class UserFilter(BaseModel):
    role: Optional[UserRole] = None
    active_only: bool = True


__all__ = ["UserRole", "UserCreate", "User", "UserFilter"]
