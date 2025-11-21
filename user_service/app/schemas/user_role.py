"""Schemas for UserRole operations with improved structure."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---------------------
# Base schema
# ---------------------
class UserRoleBase(BaseModel):
    """Base schema for user-role relationship."""

    user_id: UUID
    role_id: UUID


# ---------------------
# Create schema
# ---------------------
class UserRoleCreate(UserRoleBase):
    """Schema for creating a new user-role assignment."""


# ---------------------
# Read/Response schema
# ---------------------
class UserRoleRead(UserRoleBase):
    """Schema for reading a user-role record, includes ID and timestamps."""

    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)  # Enable ORM parsing
