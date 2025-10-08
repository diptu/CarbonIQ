# app/schemas/rbac.py
from uuid import UUID
from pydantic import BaseModel


class UserRoleAssign(BaseModel):
    role_id: UUID
    tenant_id: UUID


class UserRoleRead(BaseModel):
    user_id: UUID
    role_id: UUID
    tenant_id: UUID


class RolePermissionAssign(BaseModel):
    permission_id: UUID


class RolePermissionRead(BaseModel):
    role_id: UUID
    permission_id: UUID
