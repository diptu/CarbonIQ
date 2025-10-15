# app/tools/seed_data.py
"""Async seeder for users, roles, permissions, and associations (IMA service)."""

from __future__ import annotations
import argparse
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory, engine
from app.core.security import hash_password
from app.models.user import User, UserStatus
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.permission import Permission
from app.models.role_permission import RolePermission

# ------------------- CLI -------------------
parser = argparse.ArgumentParser()
parser.add_argument(
    "--no-truncate",
    action="store_true",
    help="Skip truncating tables before seeding",
)
parser.add_argument(
    "--password",
    type=str,
    default="Hello123",
    help="Default password for seeded users",
)
args = parser.parse_args()


# ------------------- Helpers -------------------
async def truncate_tables(session: AsyncSession) -> None:
    """Truncate relevant tables and restart identities (if exist)."""
    tables = [
        RolePermission.__tablename__,
        UserRole.__tablename__,
        User.__tablename__,
        Role.__tablename__,
        Permission.__tablename__,
    ]
    for t in tables:
        await session.execute(
            text(f"""
                DO $$
                BEGIN
                IF EXISTS (SELECT 1 FROM information_schema.tables 
                            WHERE table_name = '{t}') THEN
                    EXECUTE 'TRUNCATE TABLE {t} RESTART IDENTITY CASCADE';
                END IF;
                END$$;
                """)
        )
    await session.commit()


async def insert_roles(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Insert roles and return name -> id map with priorities."""
    roles_data = [
        ("TENANT_ADMIN", "Tenant Administrator", 1),
        ("BILLING_ADMIN", "Billing Administrator", 2),
        ("MEMBER", "Regular Member", 10),
        ("VIEWER", "Read-only User", 20),
    ]
    name_to_id: dict[str, uuid.UUID] = {}
    now = datetime.utcnow()

    for name, label, priority in roles_data:
        stmt = select(Role).where(Role.name == name)
        res = await session.execute(stmt)
        role = res.scalar_one_or_none()
        if not role:
            role = Role(
                id=uuid.uuid4(),
                name=name,
                description=label,
                is_system_role=True,
                priority=priority,
                created_at=now,
                updated_at=now,
            )
            session.add(role)
            await session.flush()
        name_to_id[name] = role.id

    await session.commit()
    return name_to_id


async def insert_permissions(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Insert permissions and return name -> id map."""
    perms_data = [
        ("view_reports", "Can view reports"),
        ("edit_resources", "Can edit resources"),
        ("manage_users", "Can manage users"),
        ("manage_billing", "Can manage billing"),
    ]
    name_to_id: dict[str, uuid.UUID] = {}
    now = datetime.utcnow()

    for code, desc in perms_data:
        stmt = select(Permission).where(Permission.code == code)
        res = await session.execute(stmt)
        perm = res.scalar_one_or_none()
        if not perm:
            perm = Permission(
                id=uuid.uuid4(),
                code=code,
                name=desc,
                description=desc,
                created_at=now,
                updated_at=now,
            )
            session.add(perm)
            await session.flush()
        name_to_id[code] = perm.id

    await session.commit()
    return name_to_id


async def insert_users(session: AsyncSession, password: str) -> dict[str, uuid.UUID]:
    """Insert users with hashed password, tenant_id, and return email -> id map."""
    hashed = hash_password(password)
    users_data = [
        ("admin@apple.com", "Alice Smith", "apple.company"),
        ("billing@orchard.apple.com", "Bob Johnson", "orchard.apple.company"),
        ("member@orchard.apple.com", "Charlie Brown", "orchard.apple.company"),
        ("viewer@orchard.apple.com", "Diana Prince", "orchard.apple.company"),
        ("admin@orange.com", "Eve Adams", "orange.company"),
        ("member@grove.orange.com", "Frank Miller", "grove.orange.company"),
        ("viewer@horizon.orange.com", "Grace Hopper", "horizon.orange.company"),
        ("admin@peanut.com", "Henry Ford", "peanut.company"),
    ]
    email_to_id: dict[str, uuid.UUID] = {}
    now = datetime.utcnow()

    for email, full_name, tenant_id in users_data:
        stmt = select(User).where(User.email == email)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=hashed,
                full_name=full_name,
                tenant_path=tenant_id,
                tenant_id=tenant_id,  # NEW
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            session.add(user)
            await session.flush()
        email_to_id[email] = user.id

    await session.commit()
    return email_to_id


async def assign_user_roles(
    session: AsyncSession, email_map: dict[str, uuid.UUID], role_map: dict[str, uuid.UUID]
) -> None:
    """Assign roles to seeded users (idempotent)."""
    assignments = [
        ("admin@apple.com", "TENANT_ADMIN"),
        ("billing@orchard.apple.com", "BILLING_ADMIN"),
        ("member@orchard.apple.com", "MEMBER"),
        ("viewer@orchard.apple.com", "VIEWER"),
        ("admin@orange.com", "TENANT_ADMIN"),
        ("member@grove.orange.com", "MEMBER"),
        ("viewer@horizon.orange.com", "VIEWER"),
        ("admin@peanut.com", "TENANT_ADMIN"),
    ]
    now = datetime.utcnow()

    for email, role_name in assignments:
        user_id = email_map[email]
        role_id = role_map[role_name]
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()
        if not existing:
            ur = UserRole(
                user_id=user_id,
                role_id=role_id,
                created_at=now,
                updated_at=now,
            )
            session.add(ur)

    await session.commit()


async def assign_role_permissions(
    session: AsyncSession, role_map: dict[str, uuid.UUID], perm_map: dict[str, uuid.UUID]
) -> None:
    """Assign permissions to roles with hierarchical inheritance (TENANT_ADMIN inherits all)."""
    role_perms = {
        "VIEWER": ["view_reports"],
        "MEMBER": ["view_reports", "edit_resources"],
        "BILLING_ADMIN": ["view_reports", "edit_resources", "manage_billing"],
        "TENANT_ADMIN": [],  # will inherit all later
    }
    now = datetime.utcnow()

    # Assign base permissions for non-admin roles
    for role_name, perms in role_perms.items():
        if role_name == "TENANT_ADMIN":
            continue
        role_id = role_map[role_name]
        for perm_code in perms:
            perm_id = perm_map[perm_code]
            stmt = select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == perm_id,
            )
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()
            if not existing:
                rp = RolePermission(
                    role_id=role_id,
                    permission_id=perm_id,
                    created_at=now,
                    updated_at=now,
                )
                session.add(rp)

    await session.flush()

    # TENANT_ADMIN inherits all permissions
    admin_id = role_map["TENANT_ADMIN"]
    all_perm_ids = [pid[0] for pid in (await session.execute(select(Permission.id))).all()]
    for perm_id in all_perm_ids:
        stmt = select(RolePermission).where(
            RolePermission.role_id == admin_id,
            RolePermission.permission_id == perm_id,
        )
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()
        if not existing:
            rp = RolePermission(
                role_id=admin_id,
                permission_id=perm_id,
                created_at=now,
                updated_at=now,
            )
            session.add(rp)

    await session.commit()


# ------------------- Main -------------------
async def main() -> None:
    async with async_session_factory() as session:
        if not args.no_truncate:
            await truncate_tables(session)

        role_map = await insert_roles(session)
        perm_map = await insert_permissions(session)
        user_map = await insert_users(session, args.password)
        await assign_user_roles(session, user_map, role_map)
        await assign_role_permissions(session, role_map, perm_map)

    await engine.dispose()
    print("✅ Seeding complete.")


if __name__ == "__main__":
    asyncio.run(main())
