"""Pydantic schemas for User operations in IMA Service with DB-driven RBAC.

Notes
-----
- `is_superuser` is readonly and only updated via direct DB operations.
- Default role is VIEWER if not explicitly assigned.
"""

from typing import List, Optional, Generic, TypeVar
from uuid import UUID
from pydantic import EmailStr, Field
from .base import ORMBase, PaginatedResponse
from .role import RoleRead


# ----------------------
# Base user schema
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
    roles : Optional[List[UUID]]
        List of role IDs assigned to the user (for input/updates).
    """

    email: EmailStr
    tenant_id: UUID
    is_active: bool = True
    is_superuser: bool = Field(
        default=False, description="Readonly; cannot be set via API", frozen=True
    )
    roles: Optional[List[UUID]] = None  # write only, IDs for assignment


# ----------------------
# User creation schema
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
    is_active: bool = True
    password: str
    # tenant_id: Optional[UUID] = None  # optional tenant for creating user

    class Config:
        orm_mode = True


# ----------------------
# User read schema
# ----------------------
class UserRead(ORMBase):
    """
    Schema for reading user information.

    Attributes
    ----------
    id : UUID
        Unique identifier of the user.
    email : EmailStr
        User's email address.
    tenant_id : UUID
        Tenant the user belongs to.
    is_active : bool
        Whether the account is active.
    is_superuser : bool
        Readonly flag for superuser status.
    roles : List[RoleRead]
        List of roles assigned to the user, with permissions.
    """

    id: UUID
    email: EmailStr
    tenant_id: UUID
    is_active: bool
    is_superuser: bool = Field(
        default=False, description="Readonly; cannot be set via API", frozen=True
    )
    roles: List[RoleRead] = []  # read-only, full role info


# ----------------------
# User update schema
# ----------------------
class UserUpdate(ORMBase):
    """
    Schema for updating user fields.

    Notes
    -----
    - `is_superuser` is readonly and not updatable via API.
    """

    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    roles: Optional[List[UUID]] = None  # IDs for role updates

    class Config:
        allow_population_by_field_name = True
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

    pass  # PaginatedResponse already defines all fields


# ----------------------
# Standardized API response schemas
# ----------------------
class UserReadResponse(ORMBase):
    """
    Standard API response for a single user read operation.

    Attributes
    ----------
    statusCode : int
        HTTP status code.
    msg : str
        Response message.
    details : UserRead
        User object details.
    """

    statusCode: int
    msg: str
    details: UserRead


class UserListResponse(ORMBase):
    """
    Standard API response for a list of users.

    Attributes
    ----------
    statusCode : int
        HTTP status code.
    msg : str
        Response message.
    details : UserList
        Paginated list of users.
    """

    statusCode: int
    msg: str
    details: UserList
