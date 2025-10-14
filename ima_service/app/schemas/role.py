"""Role schemas for the multi-tenant RBAC system with effective permissions support."""

from __future__ import annotations

import uuid
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from .base import ORMBaseSchema


class RoleStatus(str, Enum):
    """Enumeration for role status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class RoleBase(BaseModel):
    """Base schema for roles with shared attributes."""

    name: str = Field(..., max_length=100, description="Role name")
    description: Optional[str] = Field(None, description="Human-readable description")
    priority: int = Field(
        default=1, ge=1, le=100, description="Role priority (1–100, higher = more precedence)"
    )
    tenant_id: Optional[uuid.UUID] = Field(None, description="Tenant associated with this role")
    is_system_role: bool = Field(default=False, description="Indicates if role is system-defined")
    status: RoleStatus = Field(default=RoleStatus.ACTIVE, description="Role status")
    parent_role_id: Optional[uuid.UUID] = Field(
        None, description="Parent role ID for hierarchical inheritance"
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
    priority: Optional[int] = None
    # 🔑 FIX: Removed tenant_id from update. Role scope is immutable after creation.
    # tenant_id: Optional[uuid.UUID] = None
    is_system_role: Optional[bool] = None
    status: Optional[RoleStatus] = None
    parent_role_id: Optional[uuid.UUID] = None

    # 🔑 NEW: Add name validation to update schema
    _validate_name = field_validator("name", mode="before")(RoleCreate.validate_name)


class RoleRead(RoleBase, ORMBaseSchema):
    """Schema for reading role information with audit fields."""

    id: uuid.UUID = Field(..., description="Unique role identifier")
    children_ids: List[uuid.UUID] = Field(default_factory=list, description="IDs of child roles")
    effective_permission_ids: List[uuid.UUID] = Field(
        default_factory=list,
        description="Aggregated permission IDs including inherited from parent roles",
    )


class RoleInDB(RoleRead):
    """Internal schema including linked relationships for reporting."""

    user_ids: List[uuid.UUID] = Field(
        default_factory=list, description="IDs of users linked to role"
    )
    permission_ids: List[uuid.UUID] = Field(
        default_factory=list, description="IDs of permissions directly assigned to role"
    )


__all__ = [
    "RoleBase",
    "RoleCreate",
    "RoleUpdate",
    "RoleRead",
    "RoleInDB",
    "RoleStatus",
]
