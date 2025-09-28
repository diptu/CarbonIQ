from sqlalchemy.dialects.postgresql import insert
from app.db.session import async_session
from app.models.user_roles import user_roles
from app.models.user import User
from app.models.role import Role


# async def assign_role_to_user(db, user: User, role: Role):
#     stmt = insert(user_roles).values(user_id=user.id, role_id=role.id)
#     # Use PostgreSQL-specific conflict handling
#     stmt = stmt.on_conflict_do_nothing(
#         index_elements=["user_id", "role_id"]  # must match your unique constraint
#     )
#     await db.execute(stmt)
#     await db.commit()


async def assign_role_to_user(db, user, role, tenant_id=None):
    stmt = user_roles.insert().values(
        user_id=user.id, role_id=role.id, tenant_id=tenant_id
    )
    await db.execute(stmt)
    await db.commit()
