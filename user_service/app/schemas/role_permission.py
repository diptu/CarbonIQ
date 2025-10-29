"""Schemas for RolePermission operations."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


# -----------------------------
# Base
# -----------------------------
class RolePermissionBase(BaseModel):
    """Shared fields between schemas."""

    role_id: UUID = Field(..., description="Associated Role ID")
    permission_id: UUID = Field(..., description="Associated Permission ID")


# -----------------------------
# Create
# -----------------------------
class RolePermissionCreate(RolePermissionBase):
    """Schema for assigning a permission to a role."""


# -----------------------------
# Response
# -----------------------------
class RolePermissionOut(RolePermissionBase):
    """Schema for returning role-permission assignments."""

    id: UUID
    created_at: datetime
    updated_at: datetime
