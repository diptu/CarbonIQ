# app/schemas/permission.py
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    name: str = Field(..., max_length=64)
    description: Optional[str] = Field(None, max_length=255)


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=64)
    description: Optional[str] = Field(None, max_length=255)


class PermissionRead(PermissionBase):
    id: UUID

    class Config:
        orm_mode = True


class RoleRead(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


class PermissionReadWithRoles(PermissionRead):
    roles: List[RoleRead] = []
