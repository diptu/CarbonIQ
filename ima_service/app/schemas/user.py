# app/schemas/user.py
from pydantic import UUID4, EmailStr, constr
from typing import Optional
from .base import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr
    full_name: constr(min_length=1, max_length=100)
    is_active: bool = True
    tenant_id: UUID4


class UserCreate(UserBase):
    password: constr(min_length=8, max_length=128)


class UserRead(UserBase):
    id: UUID4


class UserUpdate(BaseSchema):
    full_name: Optional[constr(min_length=1, max_length=100)] = None
    password: Optional[constr(min_length=8, max_length=128)] = None
    is_active: Optional[bool] = None
