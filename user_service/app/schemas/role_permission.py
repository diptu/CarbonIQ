"""Schemas for RolePermission operations with improved structure."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------
# Base schema
# ---------------------
class RolePermissionBase(BaseModel):
    """Base schema for role-permission relationship."""

    role_id: UUID
    permission_id: UUID


# ---------------------
# Create schema
# ---------------------
class RolePermissionCreate(RolePermissionBase):
    """Schema for creating a new role-permission assignment."""


# ---------------------
# Read/Response schema
# ---------------------
class RolePermissionRead(RolePermissionBase):
    """Schema for reading a role-permission record, includes ID and timestamps."""

    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Enable ORM parsing
