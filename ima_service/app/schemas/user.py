"""Pydantic schemas for User-related operations in IMA Service."""

from typing import List, Optional
from uuid import UUID

from pydantic import EmailStr, Field

from .base import ORMBase, PaginatedResponse
from .role import RoleRead


class UserBase(ORMBase):
    """Base schema for a user."""

    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str
    is_active: bool = Field(default=True, alias="isActive")
    is_superuser: bool = Field(default=False, alias="isSuperuser")


class UserRead(ORMBase):
    """Schema for reading user information."""

    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    roles: List[RoleRead] = []


class UserUpdate(ORMBase):
    """Schema for updating user fields."""

    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = Field(default=None, alias="isActive")
    is_superuser: Optional[bool] = Field(default=None, alias="isSuperuser")

    class Config:  # pylint: disable=too-few-public-methods
        """Pydantic config for field population by alias."""

        allow_population_by_field_name = True


class UserList(PaginatedResponse[UserRead]):
    """Paginated list of users."""


class UserReadResponse(ORMBase):
    """Standard API response for a single user read operation."""

    statusCode: int
    msg: str
    details: UserRead


class UserListResponse(ORMBase):
    """Standard API response for a list of users."""

    statusCode: int
    msg: str
    details: UserList
