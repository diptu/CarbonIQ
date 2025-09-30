# mypy: ignore-errors
"""CRUD operations for Role model."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models.role import Role
from ..schemas.role import RoleCreate, RoleName


# -------------------------
# Role CRUD
# -------------------------
async def list_roles(db: AsyncSession) -> List[Role]:
    """Return all roles from the database."""
    result = await db.execute(select(Role))
    return result.scalars().all()


async def get_role_by_name(db: AsyncSession, name: RoleName) -> Optional[Role]:
    """Get role by its name."""
    result = await db.execute(select(Role).where(Role.name == name))
    return result.scalar_one_or_none()


async def get_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Role]:
    """Get roles with pagination."""
    result = await db.execute(select(Role).offset(skip).limit(limit))
    return result.scalars().all()


async def create_role(db: AsyncSession, role_in: RoleCreate) -> Role:
    """Create a new role."""
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
    """Update an existing role."""
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
    """Delete a role by ID."""
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        return False
    await db.delete(role)
    await db.commit()
    return True
