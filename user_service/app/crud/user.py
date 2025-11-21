# app/crud/user.py

"""Async CRUD operations for User model using BaseCRUD."""

from typing import Optional
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from user_service.app.crud.base import BaseCRUD
from user_service.app.models.role import Role
from user_service.app.models.user import User
from user_service.app.models.user_role import UserRole
from user_service.app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD(BaseCRUD[User, UserCreate, UserUpdate]):
    """Async CRUD for User model."""

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Retrieve a user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: UserCreate) -> User:
        """Create a new user with hashed password."""
        hashed_password = pwd_context.hash(obj_in.password)
        db_obj = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=hashed_password,
            is_active=obj_in.is_active,
            is_verified=obj_in.is_verified,
            is_superuser=obj_in.is_superuser,
        )
        return await self._commit_refresh(db, db_obj)

    async def update(self, db: AsyncSession, db_obj: User, obj_in: UserUpdate) -> User:
        """Update user fields, hash password if provided."""
        update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
        return await self._update_commit_refresh(db, db_obj, update_data)

    async def activate(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Activate a user account."""
        user = await self.get(db, user_id)
        if user:
            user.is_active = True  # type: ignore
            await db.commit()
            await db.refresh(user)
        return user

    async def deactivate(self, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Deactivate a user account."""
        user = await self.get(db, user_id)
        if user:
            user.is_active = False  # type: ignore
            await db.commit()
            await db.refresh(user)
        return user

    async def get_roles(self, user: User) -> list[str]:
        """Return all role names assigned to the user."""
        return user.roles_cached

    async def get_permissions(self, user: User) -> list[str]:
        """Return all permission names assigned to the user."""
        return user.permissions_cached

    async def get_by_email_with_roles(self, db: AsyncSession, email: str) -> User | None:
        stmt = (
            select(User)
            .options(
                selectinload(User.roles).selectinload(UserRole.role).selectinload(Role.permissions)
            )
            .where(User.email == email)
        )
        result = await db.execute(stmt)
        return result.scalars().first()


user_crud = UserCRUD(User)
