"""Role Service"""

from typing import Optional

from ..models.role import Role
from ..models.permission import Permission
from .crud_service import CRUDService


class RoleService(CRUDService[Role]):
    """Service for managing roles."""

    async def add_permission_to_role(
        self, role_id: str, permission: Permission
    ) -> None:
        """Assign a permission object to a role (within a transaction)."""
        async with self.transaction():
            role: Optional[Role] = await self.get_by_id(Role, role_id)
            if not role:
                raise ValueError(f"Role {role_id} not found")

            if permission not in role.permissions:
                role.permissions.append(permission)
                await self.update(role)
