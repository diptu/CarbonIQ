"""Users API schemas (role enum + compact I/O with examples)."""

from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    Owner = "owner"
    Editor = "editor"
    VIEWER = "viewer"


class UserCreateIn(BaseModel):
    email: EmailStr = Field(..., examples=["user@example.com"])
    password: str = Field(..., min_length=6, max_length=128, examples=["p@55w0rd"])
    role: UserRole = Field(default=UserRole.VIEWER, examples=["viewer"])
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"email": "user@example.com", "password": "p@55w0rd", "role": "viewer"}
            ]
        }
    }


class UserOut(BaseModel):
    id: str = Field(..., examples=["u-0001"])
    email: Optional[EmailStr] = Field(None, examples=["user@example.com"])
    role: UserRole = Field(..., examples=["viewer"])
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"id": "u-0001", "email": "user@example.com", "role": "viewer"}
            ]
        }
    }


__all__ = ["UserRole", "UserCreateIn", "UserOut"]
