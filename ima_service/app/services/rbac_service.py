# app/services/rbac_service.py
from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.role import Role
from app.models.permission import Permission
from app.models.user_roles import UserRole
from app.models.role_permission import RolePermission


class RBACService:
    """Role-Based Access Control service for multi-tenant applications."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------
    # User Roles
    # -------------------------------
    async def get_user_roles(self, user_id: UUID) -> List[Role]:
        """Return list of roles assigned to a user."""
        stmt = (
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def user_has_role(self, user_id: UUID, role_name: str) -> bool:
        """Check if a user has a specific role."""
        stmt = (
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id, Role.name == role_name)
        )
        result = await self.db.execute(stmt)
        role = result.scalar_one_or_none()
        return bool(role)

    # -------------------------------
    # Permissions
    # -------------------------------
    async def get_user_permissions(self, user_id: UUID) -> List[Permission]:
        """Return list of permissions assigned via roles."""
        stmt = (
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def user_has_permission(self, user_id: UUID, permission_name: str) -> bool:
        """Check if a user has a specific permission."""
        stmt = (
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, Permission.name == permission_name)
        )
        result = await self.db.execute(stmt)
        perm = result.scalar_one_or_none()
        return bool(perm)

    # -------------------------------
    # Convenience
    # -------------------------------
    async def assign_role_to_user(self, user_id: UUID, role_id: UUID, tenant_id: UUID):
        """Assign a role to a user (tenant-aware)."""
        from app.models.user_roles import UserRole

        ur = UserRole(user_id=user_id, role_id=role_id, tenant_id=tenant_id)
        self.db.add(ur)
        await self.db.commit()

    async def remove_role_from_user(self, user_id: UUID, role_id: UUID):
        """Remove a role from a user."""
        stmt = select(UserRole).where(
            UserRole.user_id == user_id, UserRole.role_id == role_id
        )
        result = await self.db.execute(stmt)
        ur = result.scalar_one_or_none()
        if ur:
            await self.db.delete(ur)
            await self.db.commit()
