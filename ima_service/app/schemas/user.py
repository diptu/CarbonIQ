# app/schemas/user.py
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from .tenant import TenantRead
from .role import RoleRead


class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    tenant_id: UUID


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    tenant_id: Optional[UUID] = None


class UserOut(UserBase):
    id: UUID
    tenant: TenantRead
    roles: List[RoleRead] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserSummary(BaseModel):
    id: UUID
    email: EmailStr
    roles: List[str] = []

    class Config:
        orm_mode = True
