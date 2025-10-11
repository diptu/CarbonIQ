"""Role schemas for the multi-tenant RBAC system."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .base import ORMBaseSchema


class RoleBase(BaseModel):
    """Base schema with shared role fields."""

    name: str = Field(..., max_length=100, description="Role name")
    description: Optional[str] = Field(None, description="Human-readable description")
    label: int = Field(default=1, description="Numeric label for ordering")
    tenant_id: Optional[uuid.UUID] = Field(
        None, description="Tenant associated with this role"
    )
    is_system_role: bool = Field(
        default=False, description="Indicates if role is system-defined"
    )


class RoleCreate(RoleBase):
    """Schema for creating a new role."""

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Ensure role name is not empty."""
        if not value.strip():
            raise ValueError("Role name cannot be empty.")
        return value


class RoleUpdate(BaseModel):
    """Schema for updating an existing role (PATCH semantics)."""

    name: Optional[str] = None
    description: Optional[str] = None
    label: Optional[int] = None
    tenant_id: Optional[uuid.UUID] = None
    is_system_role: Optional[bool] = None


class RoleRead(RoleBase, ORMBaseSchema):
    """Schema for reading role information."""

    id: uuid.UUID = Field(..., description="Unique role identifier")


class RoleInDB(RoleRead):
    """Internal schema including linked relationships."""

    user_ids: list[uuid.UUID] = Field(
        default_factory=list, description="IDs of users linked to role"
    )
    permission_ids: list[uuid.UUID] = Field(
        default_factory=list, description="IDs of permissions linked to role"
    )


__all__ = [
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleRead",
    "RoleInDB",
]
