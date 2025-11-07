"""Schemas for UserRolePermission operations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserRolePermissionBase(BaseModel):
    """Base schema for user-role-permission relationship."""

    user_id: UUID
    role_id: UUID
    permission_id: UUID


class UserRolePermissionCreate(UserRolePermissionBase):
    """Schema for creating a new user-role-permission relationship."""


class UserRolePermissionUpdate(UserRolePermissionBase):
    """Schema for creating a new user-role-permission relationship."""


class UserRolePermissionRead(UserRolePermissionBase):
    """Schema for reading a user-role-permission record, includes ID."""

    id: UUID
    model_config = ConfigDict(from_attributes=True)
