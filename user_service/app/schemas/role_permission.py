"""Schemas for UserRole and RolePermission operations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------
# RolePermission Schemas
# ---------------------
class RolePermissionBase(BaseModel):
    """Base schema for role-permission relationship."""

    role_id: UUID
    permission_id: UUID


class RolePermissionCreate(RolePermissionBase):
    """Schema for creating a new role-permission assignment."""


class RolePermissionRead(RolePermissionBase):
    """Schema for reading a role-permission record, includes ID."""

    id: UUID
    model_config = ConfigDict(from_attributes=True)
