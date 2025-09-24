# app/crud/user.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from ima_service.app.models.user import User
from ima_service.app.schemas.user import UserCreate
from ima_service.app.utils.security import get_password_hash


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(
        email=user.email,
        hashed_password=get_password_hash(user.password),
        is_active=True,
        is_superuser=False,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
) -> List[User]:
    query = select(User).offset(skip).limit(limit)
    if is_active is not None:
        query = query.filter(User.is_active.is_(is_active))
    result = await db.execute(query)
    return result.scalars().all()


async def deactivate_user(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if user:
        user.is_active = False
        await db.commit()
        await db.refresh(user)
    return user


async def reactivate_user(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalars().first()
    if user:
        user.is_active = True
        await db.commit()
        await db.refresh(user)
    return user
