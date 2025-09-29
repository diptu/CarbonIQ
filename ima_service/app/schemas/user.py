# app / schemas/user.py
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from .base import ORMBase, PaginatedResponse
from .role import RoleRead


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(UserBase):
    password: str
    is_active: bool = Field(default=True, alias="isActive")
    is_superuser: bool = Field(default=False, alias="isSuperuser")


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    is_superuser: bool
    roles: List[RoleRead] = []


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = Field(default=None, alias="isActive")
    is_superuser: Optional[bool] = Field(default=None, alias="isSuperuser")

    class Config:
        allow_population_by_field_name = True


class UserList(PaginatedResponse[UserRead]):
    pass


class UserReadResponse(BaseModel):
    statusCode: int
    msg: str
    details: UserRead


class UserListResponse(BaseModel):
    statusCode: int
    msg: str
    details: UserList
