"""Schemas for Permission model."""

import uuid
from typing import Optional, List
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    """
    Base schema for permissions.

    Attributes
    ----------
    name : str
        Permission name (e.g., 'manage_users').
    description : Optional[str]
        Optional description for the permission.
    """

    name: str = Field(..., example="manage_users")
    description: Optional[str] = Field(None, example="Allows managing user accounts")


class PermissionCreate(PermissionBase):
    """Schema for creating a permission."""

    pass


class PermissionRead(PermissionBase):
    """Schema for reading a permission."""

    id: uuid.UUID

    class Config:
        orm_mode = True


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PermissionAssign(BaseModel):
    """Schema for assigning a permission to a role."""

    permission_id: uuid.UUID


class PermissionListResponse(BaseModel):
    """Paginated list of permissions."""

    total: int
    items: List[PermissionRead]
