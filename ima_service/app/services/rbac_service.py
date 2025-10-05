# app/services/rbac_service.py
"""RBAC assignment and utility service."""

from uuid import UUID
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_roles import UserRole
from app.models.role_permission import RolePermission


# ----------------------
# User ↔ Role assignment
# ----------------------
async def assign_roles_to_user(
    db: AsyncSession, user_id: UUID, role_ids: List[UUID], tenant_id: UUID
):
    # Remove existing roles for this tenant
    await db.execute(
        UserRole.__table__.delete().where(
            UserRole.user_id == user_id, UserRole.tenant_id == tenant_id
        )
    )
    # Assign new roles
    for role_id in role_ids:
        db.add(UserRole(user_id=user_id, role_id=role_id, tenant_id=tenant_id))
    await db.commit()


async def remove_roles_from_user(
    db: AsyncSession, user_id: UUID, role_ids: List[UUID], tenant_id: UUID
):
    await db.execute(
        UserRole.__table__.delete().where(
            UserRole.user_id == user_id,
            UserRole.role_id.in_(role_ids),
            UserRole.tenant_id == tenant_id,
        )
    )
    await db.commit()


# ----------------------
# Role ↔ Permission assignment
# ----------------------
async def assign_permissions_to_role(
    db: AsyncSession, role_id: UUID, permission_ids: List[UUID]
):
    # Remove existing permissions
    await db.execute(
        RolePermission.__table__.delete().where(RolePermission.role_id == role_id)
    )
    for perm_id in permission_ids:
        db.add(RolePermission(role_id=role_id, permission_id=perm_id))
    await db.commit()


async def remove_permissions_from_role(
    db: AsyncSession, role_id: UUID, permission_ids: List[UUID]
):
    await db.execute(
        RolePermission.__table__.delete().where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id.in_(permission_ids),
        )
    )
    await db.commit()
