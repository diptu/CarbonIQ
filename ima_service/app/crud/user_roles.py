# app/crud/user_roles.py
"""User Role Assignment CRUD operations with audit logging."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, insert

from ..models.user_roles import user_roles
from ..models.user import User
from ..models.role import Role
from ..utils.audit import log_role_assignment


async def get_user_roles(db: AsyncSession, user_id: str) -> List[str]:
    """
    Fetch role names assigned to a specific user across all tenants.

    Returns a list of role names.
    """
    stmt = (
        select(Role.name)
        .join(user_roles, Role.id == user_roles.c.role_id)
        .where(user_roles.c.user_id == user_id)
    )
    result = await db.execute(stmt)
    roles = result.scalars().all()
    return roles


async def assign_role_to_user(
    db: AsyncSession,
    user: User,
    role: Role,
    tenant_id: Optional[str] = None,
    actor_id: Optional[str] = None,
) -> None:
    """
    Assign a role to a user for a specific tenant, replacing any existing role.

    Parameters
    ----------
    db : AsyncSession
        SQLAlchemy async session.
    user : User
        Target user to assign the role.
    role : Role
        Role object to assign.
    tenant_id : Optional[str], optional
        Tenant ID if scoped role, by default None.
    actor_id : Optional[str], optional
        User ID of actor performing the assignment, for audit logging.

    Notes
    -----
    - Ensures only one role exists per tenant.
    - Automatically logs the role assignment if `actor_id` is provided.
    """
    # 1️⃣ Remove existing role for this tenant
    await db.execute(
        delete(user_roles)
        .where(user_roles.c.user_id == user.id)
        .where(user_roles.c.tenant_id == tenant_id)
    )

    # 2️⃣ Assign new role
    await db.execute(
        insert(user_roles).values(
            user_id=user.id,
            role_id=role.id,
            tenant_id=tenant_id,
        )
    )
    await db.commit()

    # 3️⃣ Audit logging
    if actor_id:
        log_role_assignment(
            actor_id=actor_id,
            target_user_id=str(user.id),
            role_name=role.name,
            tenant_id=tenant_id,
        )
