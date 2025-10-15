from __future__ import annotations
from typing import Optional, Set
from ..models.role import Role
from ..models.permission import Permission
from .crud_service import CRUDService


class RoleService(CRUDService[Role]):
    """Manage roles and permissions with RBAC safeguards."""

    # --- Role CRUD with system role protection ---
    async def update_role(self, role: Role) -> Role:
        if getattr(role, "is_system_role", False):
            raise PermissionError("System roles cannot be updated")
        return await super().update(role)

    async def delete_role(self, role: Role) -> None:
        if getattr(role, "is_system_role", False):
            raise PermissionError("System roles cannot be deleted")
        await super().soft_delete(role)

    # --- Atomic Permission Linking ---
    @CRUDService.transactional
    async def link_permission(self, role_id: str, permission: Permission) -> None:
        role = await self.get_by_id(Role, role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")
        if permission not in role.permissions:
            role.permissions.append(permission)
        await self.db.flush()

    @CRUDService.transactional
    async def unlink_permission(self, role_id: str, permission: Permission) -> None:
        role = await self.get_by_id(Role, role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")
        if permission in role.permissions:
            role.permissions.remove(permission)
        await self.db.flush()

    # --- Effective Permissions (Hierarchy) ---
    async def get_effective_permissions(
        self, role_id: str, cache: Optional[dict] = None
    ) -> Set[str]:
        cache = cache or {}
        if role_id in cache:
            return cache[role_id]

        role = await self.get_by_id(Role, role_id)
        if not role:
            return set()

        perms = {p.code for p in getattr(role, "permissions", [])}
        for parent in getattr(role, "parents", []):
            perms |= await self.get_effective_permissions(parent.id, cache)

        cache[role_id] = perms
        return perms

    # --- Historical Auditing Fields ---
    async def set_effective_dates(self, role: Role, effective_from=None, effective_to=None) -> Role:
        role.effective_from = effective_from
        role.effective_to = effective_to
        return await self.update_role(role)
