"""Schemas for UserRole and RolePermission operations."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------
# UserRole Schemas
# ---------------------
class UserRoleBase(BaseModel):
    """Base schema for user-role relationship."""

    user_id: UUID
    role_id: UUID


class UserRoleCreate(UserRoleBase):
    """Schema for creating a new user-role assignment."""


class UserRoleRead(UserRoleBase):
    """Schema for reading a user-role record, includes ID."""

    id: UUID
    model_config = ConfigDict(from_attributes=True)
