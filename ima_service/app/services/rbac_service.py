"""RBAC service for managing roles and permissions."""

from uuid import UUID

from .crud_service import CRUDService
from .role_service import RoleService
from ..models.role import Role
from ..models.permission import Permission


# pylint:disable=R0903
class RBACService:
    """Service to manage RBAC: roles, permissions, and assignments."""

    def __init__(
        self,
        role_service: RoleService,
        role_crud: CRUDService[Role],
        permission_crud: CRUDService[Permission],
    ) -> None:
        self.role_service = role_service
        self.role_crud = role_crud
        self.permission_crud = permission_crud

    async def assign_permission_to_role(
        self, role_id: UUID, permission_id: UUID
    ) -> None:
        """
        Assign a permission object to a role within a transaction.
        """
        # Get Role
        role = await self.role_crud.get_by_id(Role, str(role_id))
        if not role:
            raise ValueError(f"Role {role_id} not found")

        # Get Permission
        permission = await self.permission_crud.get_by_id(
            Permission, str(permission_id)
        )
        if not permission:
            raise ValueError(f"Permission {permission_id} not found")

        # Use RoleService to add permission object
        await self.role_service.add_permission_to_role(
            role_id=str(role_id), permission_id=permission
        )  # type: ignore
