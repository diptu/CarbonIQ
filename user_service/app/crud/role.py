# app/crud/role.py

"""Async CRUD operations for Role model using BaseCRUD."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.app.crud.base import BaseCRUD
from user_service.app.models.role import Role
from user_service.app.schemas.role import RoleCreate, RoleUpdate


class RoleCRUD(BaseCRUD[Role, RoleCreate, RoleUpdate]):
    """Async CRUD for Role model."""

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Role]:
        """Retrieve a role by its name."""
        result = await db.execute(select(Role).where(Role.name == name))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: RoleCreate) -> Role:
        """Create a new role."""
        db_obj = Role(name=obj_in.name, description=obj_in.description)
        return await self._commit_refresh(db, db_obj)


role_crud = RoleCRUD(Role)
