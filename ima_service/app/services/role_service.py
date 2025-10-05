# app/services/role_service.py
"""Role CRUD and assignment logic."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.role import Role
from app.models.user_roles import UserRole
from app.schemas.role import RoleCreate, RoleUpdate


from app.models.user_roles import UserRole
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession


# ----------------------
# Assign Role to User
# ----------------------
async def assign_role_to_user(
    db: AsyncSession, user_id: UUID, role_id: UUID, tenant_id: UUID
) -> UserRole:
    """
    Assign a role to a user within a tenant.
    """
    user_role = UserRole(user_id=user_id, role_id=role_id, tenant_id=tenant_id)
    db.add(user_role)
    await db.commit()
    await db.refresh(user_role)
    return user_role


# ----------------------
# Role CRUD
# ----------------------
async def create_role(db: AsyncSession, role_in: RoleCreate) -> Role:
    role = Role(
        name=role_in.name,
        description=role_in.description,
        level=role_in.level,
        is_system=role_in.is_system or False,
    )
    db.add(role)
    try:
        await db.commit()
        await db.refresh(role)
    except IntegrityError:
        await db.rollback()
        raise ValueError(f"Role '{role_in.name}' already exists.")
    return role


async def get_role_by_id(db: AsyncSession, role_id: UUID) -> Optional[Role]:
    result = await db.execute(select(Role).where(Role.id == role_id))
    return result.scalars().first()


async def list_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Role]:
    result = await db.execute(select(Role).offset(skip).limit(limit))
    return result.scalars().all()


async def update_role(db: AsyncSession, role: Role, updates: RoleUpdate) -> Role:
    if updates.name:
        role.name = updates.name
    if updates.level is not None:
        role.level = updates.level
    if updates.description is not None:
        role.description = updates.description

    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role: Role) -> None:
    # Optional: prevent deletion of system roles
    if role.is_system:
        raise ValueError("Cannot delete system role.")
    await db.execute(UserRole.__table__.delete().where(UserRole.role_id == role.id))
    await db.delete(role)
    await db.commit()
