"""CRUD operations for Role model."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleName

# -------------------------
# Role CRUD
# -------------------------


async def get_role_by_name(db: AsyncSession, name: RoleName) -> Optional[Role]:
    result = await db.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()


async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Role]:
    result = await db.execute(select(Role).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_role(db: AsyncSession, role_in: RoleCreate) -> Role:
    role = Role(
        name=role_in.name,
        description=role_in.description,
        is_system=role_in.is_system,
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update_role(
    db: AsyncSession, role_id: UUID, role_in: RoleCreate
) -> Optional[Role]:
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        return None

    role.name = role_in.name
    role.description = role_in.description
    role.is_system = role_in.is_system

    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role_id: UUID) -> bool:
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        return False
    await db.delete(role)
    await db.commit()
    return True
