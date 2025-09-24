"""
Schemas for user-related request and response models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Shared fields between request and response models."""

    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

    # Allow reading directly from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Schema for creating a new user (signup)."""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user details (partial)."""

    # email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


class UserRead(UserBase):
    """Schema for returning user details in API responses."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
