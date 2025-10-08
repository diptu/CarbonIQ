# app/schemas/role.py
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from .permission import PermissionBase
from .user import UserBase


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_system: Optional[bool] = True


class RoleCreate(RoleBase):
    permission_ids: Optional[List[UUID]] = []


class RoleUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_system: Optional[bool]
    permission_ids: Optional[List[UUID]] = []


class RoleRead(RoleBase):
    id: UUID
    permissions: List[PermissionBase] = []
    users: Optional[List[UserBase]] = []

    class Config:
        orm_mode = True


class RoleListResponse(BaseModel):
    roles: List[RoleRead]
    total: int
