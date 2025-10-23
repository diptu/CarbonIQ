# app/services/rbac_service.py
from __future__ import annotations
from typing import Optional, Callable, Awaitable, Set
from uuid import UUID

from .role_service import RoleService
from .crud_service import CRUDService
from ..models.role import Role
from ..models.permission import Permission
from ..models.user import User


class PermissionError(Exception):
    """Raised when a user lacks a required permission."""


PolicyHook = Callable[[str, str, Optional[str]], Awaitable[bool]]


class RBACService:
    """
    Central service for enforcing RBAC.
    Handles permission checks, role-permission linking, and optional policy hooks.
    """

    def __init__(
        self,
        role_service: RoleService,
        permission_crud: CRUDService[Permission],
        policy_hook: Optional[PolicyHook] = None,
    ) -> None:
        self.role_service = role_service
        self.db = role_service.db
        self.permission_crud = permission_crud
        self.policy_hook = policy_hook

    # ------------------------ PERMISSION LINKING ------------------------

    async def assign_permission_to_role(self, role_id: UUID, permission_id: UUID) -> None:
        """
        Atomically link a permission to a role.
        Ensures both role and permission exist before assignment.
        """
        role = await self.role_service.get_by_id(Role, str(role_id))
        if not role:
            raise ValueError(f"Role {role_id} not found")

        permission = await self.permission_crud.get_by_id(Permission, str(permission_id))
        if not permission:
            raise ValueError(f"Permission {permission_id} not found")

        await self.role_service.link_permission(str(role_id), permission)

    # ------------------------ ACCESS CHECKS ------------------------

    async def check_access(
        self, user_id: str, permission_code: str, tenant_id: Optional[str] = None
    ) -> None:
        """
        Ensure a user has the specified permission.
        Raises PermissionError if access is denied.

        Policy hook runs first; if it grants access, default RBAC check is skipped.
        """
        # Run external policy hook if defined
        if self.policy_hook and await self.policy_hook(user_id, permission_code, tenant_id):
            return

        user: User = await self.db.get(User, user_id)
        if not user or not getattr(user, "is_active", True):
            raise PermissionError(f"User {user_id} not found or inactive.")

        # Check user roles for effective permissions
        for role in getattr(user, "roles", []):
            if tenant_id and getattr(role, "tenant_id", None) != tenant_id:
                continue
            perms: Set[str] = await self.role_service.get_effective_permissions(role.id)
            if permission_code in perms:
                return

        raise PermissionError(
            f"Access denied: User {user_id} lacks '{permission_code}' permission."
        )

    # ------------------------ UTILITY METHODS ------------------------

    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """Return all effective permissions for a user across all roles."""
        user: User = await self.db.get(User, user_id)
        if not user:
            return set()

        perms: Set[str] = set()
        for role in getattr(user, "roles", []):
            perms |= await self.role_service.get_effective_permissions(role.id)
        return perms
