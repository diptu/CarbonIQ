# app/tools/seed_data.py
"""Async seeder for tenants, users, roles, permissions, and associations.

- Uses async_session from app.db.session
- Uses app.core.security.hash_password
- Truncates tables by default (use --no-truncate to skip)
- Default password is "Hello123" (override with --password)
"""

from __future__ import annotations
import argparse
import asyncio
import uuid
from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session, engine
from app.core.security import hash_password
from app.models.tenant import Tenant
from app.models.role import Role
from app.models.user import User, GenderEnum
from app.models.user_roles import UserRole
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user_permission import UserPermission

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
    """Truncate relevant tables and restart identities."""
    tables = [
        UserPermission.__tablename__,
        RolePermission.__tablename__,
        UserRole.__tablename__,
        User.__tablename__,
        Role.__tablename__,
        Permission.__tablename__,
        Tenant.__tablename__,
    ]
    for t in tables:
        await session.execute(text(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE;"))
    await session.commit()


async def insert_tenants(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Insert tenants and return name -> id map."""
    tenants_data = [
        ("Apple Inc.", "apple.carboniq.com", "tenant_apple", None),
        (
            "Orchard Apple",
            "orchard.apple.carboniq.com",
            "tenant_orchard_apple",
            "Apple Inc.",
        ),
        (
            "Summit Apple",
            "summit.apple.carboniq.com",
            "tenant_summit_apple",
            "Apple Inc.",
        ),
        (
            "Harbor Apple",
            "harbor.apple.carboniq.com",
            "tenant_harbor_apple",
            "Apple Inc.",
        ),
        ("Orange Ltd.", "orange.carboniq.com", "tenant_orange", None),
        (
            "Grove Orange",
            "grove.orange.carboniq.com",
            "tenant_grove_orange",
            "Orange Ltd.",
        ),
        (
            "Horizon Orange",
            "horizon.orange.carboniq.com",
            "tenant_horizon_orange",
            "Orange Ltd.",
        ),
        ("Peanut Corp.", "peanut.carboniq.com", "tenant_peanut", None),
    ]
    name_to_id: dict[str, uuid.UUID] = {}
    now = datetime.utcnow()

    # root tenants
    for name, domain, schema, parent_name in tenants_data:
        if parent_name is None:
            t = Tenant(
                id=uuid.uuid4(),
                name=name,
                domain=domain,
                schema_name=schema,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            session.add(t)
            await session.flush()
            name_to_id[name] = t.id

    # child tenants
    for name, domain, schema, parent_name in tenants_data:
        if parent_name is not None:
            t = Tenant(
                id=uuid.uuid4(),
                name=name,
                domain=domain,
                schema_name=schema,
                parent_id=name_to_id[parent_name],
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            session.add(t)
            await session.flush()
            name_to_id[name] = t.id

    await session.commit()
    return name_to_id


async def insert_roles(session: AsyncSession) -> dict[str, uuid.UUID]:
    """Insert roles and return name -> id map."""
    roles_data = [
        ("TENANT_ADMIN", 4, "Tenant Administrator"),
        ("BILLING_ADMIN", 3, "Billing Administrator"),
        ("MEMBER", 2, "Regular Member"),
        ("VIEWER", 1, "Read-only User"),
    ]
    name_to_id: dict[str, uuid.UUID] = {}
    now = datetime.utcnow()

    for name, label, desc in roles_data:
        stmt = select(Role).where(Role.name == name)
        res = await session.execute(stmt)
        role = res.scalar_one_or_none()
        if not role:
            role = Role(
                id=uuid.uuid4(),
                name=name,
                label=label,
                description=desc,
                is_system=True,
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

    for name, desc in perms_data:
        stmt = select(Permission).where(Permission.name == name)
        res = await session.execute(stmt)
        perm = res.scalar_one_or_none()
        if not perm:
            perm = Permission(
                id=uuid.uuid4(),
                name=name,
                description=desc,
                created_at=now,
                updated_at=now,
            )
            session.add(perm)
            await session.flush()
        name_to_id[name] = perm.id

    await session.commit()
    return name_to_id


async def insert_users(
    session: AsyncSession, password: str, tenant_map: dict[str, uuid.UUID]
) -> dict[str, uuid.UUID]:
    """Insert users with hashed password and return email -> id map."""
    hashed = hash_password(password)
    users_data = [
        (
            "admin@apple.com",
            "Apple Inc.",
            "Alice",
            "Smith",
            GenderEnum.FEMALE,
            "USA",
            True,
        ),
        (
            "billing@orchard.apple.com",
            "Orchard Apple",
            "Bob",
            "Johnson",
            GenderEnum.MALE,
            "USA",
            False,
        ),
        (
            "member@orchard.apple.com",
            "Orchard Apple",
            "Charlie",
            "Brown",
            GenderEnum.OTHER,
            "USA",
            False,
        ),
        (
            "viewer@orchard.apple.com",
            "Orchard Apple",
            "Diana",
            "Prince",
            GenderEnum.FEMALE,
            "USA",
            False,
        ),
        (
            "admin@orange.com",
            "Orange Ltd.",
            "Eve",
            "Adams",
            GenderEnum.FEMALE,
            "USA",
            True,
        ),
        (
            "member@grove.orange.com",
            "Grove Orange",
            "Frank",
            "Miller",
            GenderEnum.MALE,
            "USA",
            False,
        ),
        (
            "viewer@horizon.orange.com",
            "Horizon Orange",
            "Grace",
            "Hopper",
            GenderEnum.FEMALE,
            "USA",
            False,
        ),
        (
            "admin@peanut.com",
            "Peanut Corp.",
            "Henry",
            "Ford",
            GenderEnum.MALE,
            "USA",
            True,
        ),
    ]
    email_to_id: dict[str, uuid.UUID] = {}
    now = datetime.utcnow()

    for (
        email,
        tenant_name,
        first_name,
        last_name,
        gender,
        country,
        is_superuser,
    ) in users_data:
        tenant_id = tenant_map[tenant_name]
        stmt = select(User).where(User.email == email)
        res = await session.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=email,
                password_hash=hashed,
                tenant_id=tenant_id,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                country=country,
                is_active=True,
                is_superuser=is_superuser,
                created_at=now,
                updated_at=now,
            )
            session.add(user)
            await session.flush()
        email_to_id[email] = user.id

    await session.commit()
    return email_to_id


async def assign_user_roles(
    session: AsyncSession,
    email_map: dict[str, uuid.UUID],
    role_map: dict[str, uuid.UUID],
    tenant_map: dict[str, uuid.UUID],
) -> None:
    """Assign roles to seeded users (idempotent)."""
    assignments = [
        ("admin@apple.com", "TENANT_ADMIN", "Apple Inc."),
        ("billing@orchard.apple.com", "BILLING_ADMIN", "Orchard Apple"),
        ("member@orchard.apple.com", "MEMBER", "Orchard Apple"),
        ("viewer@orchard.apple.com", "VIEWER", "Orchard Apple"),
        ("admin@orange.com", "TENANT_ADMIN", "Orange Ltd."),
        ("member@grove.orange.com", "MEMBER", "Grove Orange"),
        ("viewer@horizon.orange.com", "VIEWER", "Horizon Orange"),
        ("admin@peanut.com", "TENANT_ADMIN", "Peanut Corp."),
    ]
    now = datetime.utcnow()

    for email, role_name, tenant_name in assignments:
        user_id = email_map[email]
        role_id = role_map[role_name]
        tenant_id = tenant_map[tenant_name]
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
            UserRole.tenant_id == tenant_id,
        )
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()
        if not existing:
            ur = UserRole(
                user_id=user_id,
                role_id=role_id,
                tenant_id=tenant_id,
                created_at=now,
                updated_at=now,
            )
            session.add(ur)

    await session.commit()


async def assign_role_permissions(
    session: AsyncSession,
    role_map: dict[str, uuid.UUID],
    perm_map: dict[str, uuid.UUID],
) -> None:
    """Assign permissions to roles (idempotent)."""
    role_perms = {
        "TENANT_ADMIN": [
            "view_reports",
            "edit_resources",
            "manage_users",
            "manage_billing",
        ],
        "BILLING_ADMIN": ["view_reports", "edit_resources", "manage_billing"],
        "MEMBER": ["view_reports", "edit_resources"],
        "VIEWER": ["view_reports"],
    }
    now = datetime.utcnow()

    for role_name, perms in role_perms.items():
        role_id = role_map[role_name]
        for perm_name in perms:
            perm_id = perm_map[perm_name]
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

    await session.commit()


async def assign_user_permissions(
    session: AsyncSession,
    email_map: dict[str, uuid.UUID],
    perm_map: dict[str, uuid.UUID],
) -> None:
    """Assign direct permissions to users (idempotent)."""
    user_perms = {
        "admin@peanut.com": ["view_reports"],
        "viewer@orchard.apple.com": ["view_reports"],
    }
    now = datetime.utcnow()

    for email, perms in user_perms.items():
        user_id = email_map[email]
        for perm_name in perms:
            perm_id = perm_map[perm_name]
            stmt = select(UserPermission).where(
                UserPermission.user_id == user_id,
                UserPermission.permission_id == perm_id,
            )
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()
            if not existing:
                up = UserPermission(
                    user_id=user_id,
                    permission_id=perm_id,
                    created_at=now,
                    updated_at=now,
                )
                session.add(up)

    await session.commit()


# ------------------- Main -------------------
async def main() -> None:
    async with async_session() as session:
        if not args.no_truncate:
            await truncate_tables(session)

        tenant_map = await insert_tenants(session)
        role_map = await insert_roles(session)
        perm_map = await insert_permissions(session)
        user_map = await insert_users(session, args.password, tenant_map)
        await assign_user_roles(session, user_map, role_map, tenant_map)
        await assign_role_permissions(session, role_map, perm_map)
        await assign_user_permissions(session, user_map, perm_map)

    await engine.dispose()
    print("✅ Seeding complete.")


if __name__ == "__main__":
    asyncio.run(main())
