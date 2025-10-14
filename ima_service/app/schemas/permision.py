"""Permission schemas for the multi-tenant RBAC system with enhanced production readiness."""

from __future__ import annotations

import uuid
from typing import Optional, List

from pydantic import BaseModel, Field, field_validator

from .base import ORMBaseSchema


class PermissionBase(BaseModel):
    """Base schema with shared permission fields."""

    code: str = Field(..., max_length=100, description="Machine-readable permission code")
    name: str = Field(..., max_length=100, description="Human-readable permission name")
    description: Optional[str] = Field(None, description="Description of permission purpose")
    module: Optional[str] = Field(None, max_length=50, description="Module or logical grouping")
    tenant_id: Optional[uuid.UUID] = Field(None, description="Tenant ID for multi-tenant scope")

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        """Ensure permission code is not empty and trimmed."""
        if not value or not value.strip():
            raise ValueError("Permission code cannot be empty.")
        return value.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Ensure permission name is not empty and trimmed."""
        if not value or not value.strip():
            raise ValueError("Permission name cannot be empty.")
        return value.strip()

    @field_validator("module")
    @classmethod
    def validate_module(cls, value: Optional[str]) -> Optional[str]:
        """Trim module string if provided."""
        return value.strip() if value else value


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""


class PermissionUpdate(BaseModel):
    """Schema for updating existing permissions (PATCH semantics)."""

    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    module: Optional[str] = None
    # 🔑 FIX: Removed tenant_id from update. Scope should be immutable after creation.
    # tenant_id: Optional[uuid.UUID] = None

    # 🔑 NEW: Add validation to update schema
    _validate_code = field_validator("code", mode="before")(PermissionBase.validate_code)
    _validate_name = field_validator("name", mode="before")(PermissionBase.validate_name)
    _validate_module = field_validator("module", mode="before")(PermissionBase.validate_module)


class PermissionRead(PermissionBase, ORMBaseSchema):
    """Schema for reading permission data with ID, full audit fields, and derived data."""

    id: uuid.UUID = Field(..., description="Unique permission identifier")
    # Optional computed field: users having this permission via roles
    effective_user_ids: List[uuid.UUID] = Field(
        default_factory=list, description="IDs of users with this permission via roles"
    )
    # The inherited ORMBaseSchema now includes:
    # created_at, updated_at, deleted_at, tenant_id, created_by, updated_by


class PermissionInDB(PermissionRead):
    """Internal schema including linked relationships and full audit info."""

    role_ids: List[uuid.UUID] = Field(
        default_factory=list, description="roles linked to permission"
    )
    # 🔑 FIX: Removed redundant audit fields;
    #  they are inherited from PermissionRead (via ORMBaseSchema)
    # created_by: Optional[uuid.UUID] = Field(
    # None,description="User ID who created this permission")
    # updated_by: Optional[uuid.UUID] = Field(
    # None, description="User ID who last updated this permission")


__all__ = [
    "PermissionBase",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionRead",
    "PermissionInDB",
]
