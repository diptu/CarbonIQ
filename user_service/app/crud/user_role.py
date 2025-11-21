# app/crud/user_role.py

"""Async CRUD operations for UserRole model using BaseCRUD."""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.app.crud.base import BaseCRUD
from user_service.app.models.user_role import UserRole
from user_service.app.schemas.user_role import UserRoleCreate


class UserRoleCRUD(BaseCRUD[UserRole, UserRoleCreate, UserRoleCreate]):
    """Async CRUD for UserRole model."""

    async def get_by_user_role(
        self, db: AsyncSession, user_id: UUID, role_id: UUID
    ) -> Optional[UserRole]:
        """Retrieve a UserRole by user_id and role_id."""
        result = await db.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: UserRoleCreate) -> UserRole:
        """Create a UserRole only if it does not exist."""
        existing = await self.get_by_user_role(db, obj_in.user_id, obj_in.role_id)
        if existing:
            return existing
        db_obj = UserRole(user_id=obj_in.user_id, role_id=obj_in.role_id)
        return await self._commit_refresh(db, db_obj)


user_role_crud = UserRoleCRUD(UserRole)
