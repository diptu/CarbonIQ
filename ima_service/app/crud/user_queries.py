# app/crud/user_queries.py
"""Utility queries for users with roles preloading."""

from typing import List, Optional, cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..models.user import User


# -------------------------
# User queries with roles preloaded
# -------------------------
async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Retrieve a user by email, preloading roles.

    Parameters
    ----------
    db : AsyncSession
        Async database session.
    email : str
        Email address of the user.

    Returns
    -------
    Optional[User]
        User object if found, else None.
    """
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.email == email)
    )
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Retrieve a user by UUID, preloading roles.

    Parameters
    ----------
    db : AsyncSession
        Async database session.
    user_id : UUID
        Unique identifier of the user.

    Returns
    -------
    Optional[User]
        User object if found, else None.
    """
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.id == user_id)
    )
    return result.scalars().first()


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
) -> List[User]:
    """Retrieve a paginated list of users with optional active filter and roles preloaded.

    Parameters
    ----------
    db : AsyncSession
        Async database session.
    skip : int
        Number of records to skip.
    limit : int
        Maximum number of records to return.
    is_active : Optional[bool]
        Filter by active status if provided.

    Returns
    -------
    List[User]
        List of user objects.
    """
    query = select(User).options(selectinload(User.roles)).offset(skip).limit(limit)
    if is_active is not None:
        query = query.where(User.is_active.is_(is_active))

    result = await db.execute(query)
    return cast(List[User], result.scalars().all())
