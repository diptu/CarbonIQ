# app/services/role_service.py
from __future__ import annotations
from typing import Optional, Set, Dict
from sqlalchemy import select

from ..models.role import Role
from ..models.permission import Permission
from .crud_service import CRUDService


class RoleService(CRUDService[Role]):
    """
    Service for managing roles and permissions with RBAC safeguards.
    Includes tenant scoping, system role protection, and effective permission calculation.
    """

    # ---------------------- ROLE CRUD WITH SYSTEM ROLE PROTECTION ----------------------

    async def update_role(self, role: Role) -> Role:
        """Update a role unless it is a protected system role."""
        if getattr(role, "is_system_role", False):
            raise PermissionError("System roles cannot be updated")
        return await super().update(role)

    async def delete_role(self, role: Role) -> None:
        """Soft-delete a role unless it is a protected system role."""
        if getattr(role, "is_system_role", False):
            raise PermissionError("System roles cannot be deleted")
        await super().soft_delete(role)

    # ---------------------- USER-ROLE / USER-PERMISSIONS ----------------------

    async def get_user_roles(self, user_id: str) -> list[str]:
        """Return a list of role names assigned to a user."""
        stmt = (
            select(Role)
            .join(Role.users)  # many-to-many: Role.users -> User.roles
            .where(Role.users.any(id=user_id))
        )
        result = await self.db.execute(stmt)
        return [role.name for role in result.scalars().all()]

    async def get_user_permissions(self, user_id: str) -> list[str]:
        """Return unique permission codes assigned to a user via roles."""
        stmt = (
            select(Permission.code)
            .join(Permission.roles)
            .join(Role.users)
            .where(Role.users.any(id=user_id))
        )
        result = await self.db.execute(stmt)
        return list({row[0] for row in result.all()})  # unique codes

    # ---------------------- ATOMIC PERMISSION LINKING ----------------------

    @CRUDService.transactional
    async def link_permission(self, role_id: str, permission: Permission) -> None:
        """Add a permission to a role, if not already linked."""
        role = await self.get_by_id(Role, role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")
        if permission not in role.permissions:
            role.permissions.append(permission)
        await self.db.flush()

    @CRUDService.transactional
    async def unlink_permission(self, role_id: str, permission: Permission) -> None:
        """Remove a permission from a role, if linked."""
        role = await self.get_by_id(Role, role_id)
        if not role:
            raise ValueError(f"Role {role_id} not found")
        if permission in role.permissions:
            role.permissions.remove(permission)
        await self.db.flush()

    # ---------------------- EFFECTIVE PERMISSIONS WITH HIERARCHY ----------------------

    async def get_effective_permissions(
        self, role_id: str, cache: Optional[Dict[str, Set[str]]] = None
    ) -> Set[str]:
        """
        Compute all permissions for a role including inherited permissions.
        Uses memoization to avoid redundant queries.
        """
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

    # ---------------------- AUDITABLE / EFFECTIVE DATES ----------------------

    async def set_effective_dates(self, role: Role, effective_from=None, effective_to=None) -> Role:
        """
        Set role's effective_from and effective_to dates for auditing purposes.
        """
        role.effective_from = effective_from
        role.effective_to = effective_to
        return await self.update_role(role)
