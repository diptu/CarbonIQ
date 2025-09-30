"""User Role Assignement"""

from ..models.user_roles import user_roles


async def assign_role_to_user(db, user, role, tenant_id=None):
    """Assigne Role to a User"""
    stmt = user_roles.insert().values(
        user_id=user.id, role_id=role.id, tenant_id=tenant_id
    )
    await db.execute(stmt)
    await db.commit()
