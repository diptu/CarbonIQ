from typing import List
from uuid import UUID
from pydantic import EmailStr
from .base import ORMBase
from .role import RoleRead


# Base user fields
class UserBase(ORMBase):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False


# For creating a new user
class UserCreate(UserBase):
    password: str


# For returning a single user
class UserRead(UserBase):
    id: UUID
    roles: List[RoleRead] = []

    model_config = {
        "from_attributes": True  # Pydantic v2 ORM support
    }


# For returning a paginated list of users
class UserListResponse(ORMBase):
    total: int
    previousPage: str | None
    nextPage: str | None
    users: List[UserRead]
