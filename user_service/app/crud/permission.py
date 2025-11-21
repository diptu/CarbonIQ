# app/crud/permission.py

"""Async CRUD operations for Permission model using BaseCRUD."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.app.crud.base import BaseCRUD
from user_service.app.models.permission import Permission
from user_service.app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionCRUD(BaseCRUD[Permission, PermissionCreate, PermissionUpdate]):
    """Async CRUD for Permission model."""

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Permission]:
        """Retrieve a permission by its name."""
        result = await db.execute(select(Permission).where(Permission.name == name))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: PermissionCreate) -> Permission:
        """Create a new permission record."""
        db_obj = Permission(name=obj_in.name, description=obj_in.description)
        return await self._commit_refresh(db, db_obj)


permission_crud = PermissionCRUD(Permission)
