# app/crud/role_permission.py

"""Async CRUD operations for RolePermission model using BaseCRUD."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.app.crud.base import BaseCRUD
from user_service.app.models.role_permission import RolePermission
from user_service.app.schemas.role_permission import RolePermissionCreate


class RolePermissionCRUD(BaseCRUD[RolePermission, RolePermissionCreate, RolePermissionCreate]):
    """Async CRUD for RolePermission model."""

    async def get_by_role_permission(
        self, db: AsyncSession, role_id: UUID, permission_id: UUID
    ) -> Optional[RolePermission]:
        """Retrieve a RolePermission by role_id and permission_id."""
        result = await db.execute(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: RolePermissionCreate) -> RolePermission:
        """Create a new RolePermission, avoiding duplicates."""
        existing = await self.get_by_role_permission(db, obj_in.role_id, obj_in.permission_id)
        if existing:
            return existing
        db_obj = RolePermission(role_id=obj_in.role_id, permission_id=obj_in.permission_id)
        return await self._commit_refresh(db, db_obj)


role_permission_crud = RolePermissionCRUD(RolePermission)
