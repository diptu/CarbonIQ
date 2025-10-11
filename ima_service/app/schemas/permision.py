"""Permission schemas for the multi-tenant RBAC system."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .base import ORMBaseSchema


class PermissionBase(BaseModel):
    """Base schema with shared permission fields."""

    name: str = Field(..., max_length=100, description="Permission name")
    description: Optional[str] = Field(
        None, description="Description of permission purpose"
    )


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Ensure permission name is not empty."""
        if not value.strip():
            raise ValueError("Permission name cannot be empty.")
        return value


class PermissionUpdate(BaseModel):
    """Schema for updating existing permissions (PATCH semantics)."""

    name: Optional[str] = None
    description: Optional[str] = None


class PermissionRead(PermissionBase, ORMBaseSchema):
    """Schema for reading permission data."""

    id: uuid.UUID = Field(..., description="Unique permission identifier")


class PermissionInDB(PermissionRead):
    """Internal schema including linked relationships."""

    role_ids: list[uuid.UUID] = Field(
        default_factory=list, description="IDs of roles linked to permission"
    )


__all__ = [
    "PermissionBase",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionRead",
    "PermissionInDB",
]
