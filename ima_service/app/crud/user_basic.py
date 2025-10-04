# app/crud/user_basic
"""Basic User CRUD operations with UUID and role preloading."""

from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from ..models.role import Role
from ..models.user import User
from ..models.user_roles import user_roles
from ..schemas.role import RoleRead
from ..schemas.user import UserCreate, UserUpdate
from ..utils.security import get_password_hash


# -------------------------
# User CRUD
# -------------------------
async def update_user_role(
    db: AsyncSession,
    user: User,
    existing_role: Role,
    new_role: Role,
    tenant_id: Optional[str] = None,
) -> None:
    """Update a user's role for a given tenant in the user_roles table."""
    stmt = (
        update(user_roles)
        .where(user_roles.c.user_id == user.id)
        .where(user_roles.c.role_id == existing_role.id)
    )
    if tenant_id is not None:
        stmt = stmt.where(user_roles.c.tenant_id == tenant_id)
    else:
        stmt = stmt.where(user_roles.c.tenant_id.is_(None))

    stmt = stmt.values(role_id=new_role.id)
    await db.execute(stmt)
    await db.commit()


async def update_user(db: AsyncSession, user: User, user_in: UserUpdate) -> User:
    """Update a user’s email, password, superuser status, or active flag."""
    if user_in.email is not None:
        user.email = user_in.email
    if user_in.is_superuser is not None:
        user.is_superuser = user_in.is_superuser
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.password:
        user.hashed_password = get_password_hash(user_in.password)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Find a user based on their email with roles preloaded."""
    result = await db.execute(
        select(User).options(selectinload(User.roles)).where(User.email == email)
    )
    return result.scalars().first()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a user with hashed password."""
    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=user_in.is_active,
        is_superuser=user_in.is_superuser,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


def user_to_schema(user: User) -> dict[str, object]:
    """Convert SQLAlchemy User -> UserRead compatible dict."""
    return {
        "id": user.id,
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "roles": [RoleRead.from_orm(r) for r in getattr(user, "roles", [])],
    }


async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def list_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Tuple[int, List[User]]:
    """List users with pagination, returns total count and user list."""
    # Total count query
    total_result = await db.execute(select(func.count(User.id)))
    total: int = total_result.scalar_one()

    # Users query with offset & limit
    result = await db.execute(select(User).offset(skip).limit(limit))
    users: List[User] = list(result.scalars())

    return total, users


async def deactivate_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Deactivate a user based on UUID."""
    user = await get_user(db, user_id)
    if user:
        user.is_active = False
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def reactivate_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Reactivate a user based on UUID."""
    user = await get_user(db, user_id)
    if user:
        user.is_active = True
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    """Delete a user based on UUID."""
    user = await get_user(db, user_id)
    if not user:
        return False
    await db.delete(user)
    await db.commit()
    return True
