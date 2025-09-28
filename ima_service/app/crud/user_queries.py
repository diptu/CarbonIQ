"""Utility queries for users with roles preloading."""

from typing import List, Optional, cast
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.user import User

# -------------------------
# User queries with roles preloaded
# -------------------------


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.email == email)
    )
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    return result.scalars().first()


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
) -> List[User]:
    query = select(User).options(selectinload(User.roles)).offset(skip).limit(limit)
    if is_active is not None:
        query = query.where(User.is_active.is_(is_active))
    result = await db.execute(query)
    return cast(List[User], result.scalars().all())
