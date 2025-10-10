# app/schemas/rbac.py
from pydantic import UUID4
from .base import BaseSchema


class UserRoleAssign(BaseSchema):
    user_id: UUID4
    role_id: UUID4
    tenant_id: UUID4


class RolePermissionAssign(BaseSchema):
    role_id: UUID4
    permission_id: UUID4
