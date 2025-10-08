# app/services/permission_service.py
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionService:
    """Service to manage permissions and role-permission assignments."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------
    # Permission CRUD
    # -------------------------------
    async def create_permission(self, perm_in: PermissionCreate) -> Permission:
        """Create a new permission."""
        perm = Permission(
            id=uuid4(),
            name=perm_in.name,
            description=perm_in.description,
            tenant_id=perm_in.tenant_id,
        )
        self.db.add(perm)
        try:
            await self.db.commit()
            await self.db.refresh(perm)
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("Permission with this name already exists in the tenant")
        return perm

    async def get_permission(self, permission_id: UUID) -> Optional[Permission]:
        """Fetch a permission by ID."""
        stmt = select(Permission).where(Permission.id == permission_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_permissions(
        self, tenant_id: Optional[UUID] = None
    ) -> List[Permission]:
        """List all permissions, optionally filtered by tenant."""
        stmt = select(Permission)
        if tenant_id:
            stmt = stmt.where(Permission.tenant_id == tenant_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_permission(
        self, permission_id: UUID, perm_in: PermissionUpdate
    ) -> Permission:
        """Update a permission."""
        perm = await self.get_permission(permission_id)
        if not perm:
            raise ValueError("Permission not found")

        for field, value in perm_in.model_dump(exclude_unset=True).items():
            setattr(perm, field, value)

        self.db.add(perm)
        await self.db.commit()
        await self.db.refresh(perm)
        return perm

    async def delete_permission(self, permission_id: UUID) -> None:
        """Delete a permission."""
        perm = await self.get_permission(permission_id)
        if not perm:
            raise ValueError("Permission not found")

        await self.db.delete(perm)
        await self.db.commit()

    # -------------------------------
    # Role-Permission Assignment
    # -------------------------------
    async def assign_permission_to_role(self, role_id: UUID, permission_id: UUID):
        """Assign a permission to a role."""
        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        self.db.add(rp)
        await self.db.commit()

    async def remove_permission_from_role(self, role_id: UUID, permission_id: UUID):
        """Remove a permission from a role."""
        stmt = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id,
        )
        result = await self.db.execute(stmt)
        rp = result.scalar_one_or_none()
        if rp:
            await self.db.delete(rp)
            await self.db.commit()
