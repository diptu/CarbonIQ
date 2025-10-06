# app/services/user_service.py
"""User-related business logic for IMA Service."""

from typing import List, Optional
from uuid import UUID
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.models.role import Role
from app.models.user_roles import UserRole
from app.models.user_roles import UserRole
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)


# ----------------------
# User CRUD
# ----------------------
async def create_user(
    db: AsyncSession,
    user_in: UserCreate,
    tenant_id: UUID,
    default_role_id: Optional[UUID] = None,
) -> User:
    """Create a new user and assign roles."""
    hashed_pwd = hash_password(user_in.password)
    user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        is_active=user_in.is_active,
        tenant_id=tenant_id,
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise ValueError(f"User with email {user_in.email} already exists.")

    # Assign roles
    role_ids = user_in.roles or ([default_role_id] if default_role_id else [])
    for role_id in role_ids:
        db.add(UserRole(user_id=user.id, role_id=role_id, tenant_id=tenant_id))
    if role_ids:
        await db.commit()

    return user


from sqlalchemy import func


# list_users function
async def list_users(
    db: AsyncSession, skip: int = 0, limit: int = 10, tenant_id: UUID | None = None
):
    """
    Return total count and a list of users, optionally filtered by tenant_id.
    """
    query = select(User)
    if tenant_id:
        query = query.where(User.tenant_id == tenant_id)

    result = await db.execute(query.offset(skip).limit(limit))
    users = result.scalars().all()

    # Total count
    total_query = select(User)
    if tenant_id:
        total_query = total_query.where(User.tenant_id == tenant_id)
    total_result = await db.execute(total_query)
    total = len(total_result.scalars().all())

    return total, users


async def get_user_by_email(
    db: AsyncSession, email: str, tenant_id: Optional[UUID] = None
) -> Optional[User]:
    query = select(User).where(User.email == email)
    if tenant_id:
        query = query.where(User.tenant_id == tenant_id)
    result = await db.execute(query)
    return result.scalars().first()


async def authenticate_user(
    db: AsyncSession, email: str, password: str, tenant_id: Optional[UUID] = None
) -> Optional[User]:
    user = await get_user_by_email(db, email, tenant_id)
    if (
        not user
        or not verify_password(password, user.hashed_password)
        or not user.is_active
    ):
        return None
    return user


def create_tokens_for_user(user: User, roles: List[str]) -> dict:
    access_token = create_access_token(
        user_id=user.id, tenant_id=user.tenant_id, roles=roles
    )
    refresh_token = create_refresh_token(user_id=user.id, tenant_id=user.tenant_id)

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "tokenType": "Bearer",
        "expiresIn": 3600,
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "roles": roles,
    }
