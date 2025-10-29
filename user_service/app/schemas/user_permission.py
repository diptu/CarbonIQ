"""Schemas for UserPermission operations."""

from uuid import UUID

from pydantic import BaseModel


class UserPermissionBase(BaseModel):
    """Base schema for user-permission relationship."""

    user_id: UUID
    permission_id: UUID


class UserPermissionCreate(UserPermissionBase):
    """Schema for creating a new user-permission relationship."""


class UserPermissionRead(UserPermissionBase):
    """Schema for reading a user-permission relationship, includes ID."""

    id: UUID
