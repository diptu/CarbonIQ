# app/crud/user_roles.py
"""User Role Assignment CRUD operations with audit logging."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user_roles import user_roles
from ..models.user import User
from ..models.role import Role
from ..utils.audit import log_role_assignment
from typing import List
from sqlalchemy import select


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
    Assign a role to a user for a specific tenant, with audit logging.

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
    - Automatically logs the role assignment if `actor_id` is provided.
    """
    stmt = user_roles.insert().values(
        user_id=user.id,
        role_id=role.id,
        tenant_id=tenant_id,
    )
    await db.execute(stmt)
    await db.commit()

    # Audit logging
    if actor_id:
        log_role_assignment(
            actor_id=actor_id,
            target_user_id=str(user.id),
            role_name=role.name,
            tenant_id=tenant_id,
        )
