"""Pydantic schemas for User operations in IMA Service with DB-driven RBAC.

Notes
-----
- `is_superuser` is readonly and only updated via direct DB operations.
- Default role is VIEWER if not explicitly assigned.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import EmailStr, Field
from .base import ORMBase, PaginatedResponse
from .role import RoleRead


# ----------------------
# Base user schema (shared fields)
# ----------------------
class UserBase(ORMBase):
    """
    Base schema for a user.

    Attributes
    ----------
    email : EmailStr
        User's email address.
    tenant_id : UUID
        ID of the tenant the user belongs to.
    is_active : bool
        Whether the user account is active.
    is_superuser : bool
        Readonly; bypasses RBAC checks if True.
    created_by : Optional[UUID]
        User ID of the creator (read-only).
    """

    email: EmailStr
    tenant_id: UUID
    is_active: bool = True
    is_superuser: bool = Field(
        default=False, description="Readonly; cannot be set via API", frozen=True
    )
    created_by: Optional[UUID] = Field(
        default=None, description="User ID of the creator", frozen=True
    )


# ----------------------
# User creation schema (input)
# ----------------------
class UserCreate(ORMBase):
    """
    Schema for creating a new user.

    Notes
    -----
    - `is_superuser` is NOT settable via API.
    - Default role VIEWER is assigned if roles not provided.
    """

    email: EmailStr
    password: str
    is_active: bool = True
    roles: Optional[List[UUID]] = None  # role IDs to assign
    tenant_id: Optional[UUID] = None  # optional, defaults to current user's tenant

    class Config:
        orm_mode = True


# ----------------------
# User update schema (input)
# ----------------------
class UserUpdate(ORMBase):
    """
    Schema for updating user fields.

    Notes
    -----
    - `is_superuser` is readonly and not updatable via API.
    """

    password: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[UUID]] = None  # role IDs for updates

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


# ----------------------
# User read schema (output)
# ----------------------
class UserRead(UserBase):
    """
    Schema for reading user information.

    Attributes
    ----------
    id : UUID
        Unique identifier of the user.
    roles : List[RoleRead]
        List of roles assigned to the user, with permissions.
    """

    id: UUID
    roles: List[RoleRead] = []  # override base roles with full role info

    class Config:
        orm_mode = True


# ----------------------
# Paginated user list
# ----------------------
class UserList(PaginatedResponse[UserRead]):
    """
    Paginated list of users.

    Attributes
    ----------
    items : List[UserRead]
        Users in the current page.
    """

    pass


# ----------------------
# Standardized API response schemas
# ----------------------
class UserReadResponse(ORMBase):
    """
    Standard API response for a single user read operation.
    """

    statusCode: int
    msg: str
    details: UserRead


class UserListResponse(ORMBase):
    """
    Standard API response for a list of users.
    """

    statusCode: int
    msg: str
    details: UserList
