# app/services/user_service.py
"""User-related business logic for IMA Service."""

from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime

from app.models.user import User
from app.models.role import Role
from app.models.user_roles import UserRole
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def get_accessible_tenants(user_tenant_id: str, db: AsyncSession) -> list[str]:
    """
    Return list of tenant IDs accessible to this user:
    - Own tenant
    - All child tenants (if any)
    """
    query = text("""
    WITH RECURSIVE child_tenants AS (
        SELECT id
        FROM tenants
        WHERE id = :tenant_id
        UNION ALL
        SELECT t.id
        FROM tenants t
        INNER JOIN child_tenants ct ON t.parent_id = ct.id
    )
    SELECT id FROM child_tenants;
    """)
    result = await db.execute(query, {"tenant_id": user_tenant_id})
    tenant_ids = [str(tid) for tid in result.scalars().all()]
    return tenant_ids


# ---------------------------------------------------------------------------
# 🧩 User CREATE
# ---------------------------------------------------------------------------
async def get_role_by_name(db: AsyncSession, name: str, tenant_id: UUID) -> Role:
    """Fetch a role by name within a tenant."""
    q = select(Role).where(Role.name == name, Role.tenant_id == tenant_id)
    result = await db.execute(q)
    role = result.scalar_one_or_none()
    if not role:
        raise ValueError(f"Role {name} not found in tenant {tenant_id}")
    return role


# app/services/user_service.py


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    tenant_id: str,  # remove creator_tenant_id
):
    """Create a new user under a tenant and assign default VIEWER role."""

    # Hash password
    hashed_password = hash_password(password)

    # Create User object
    new_user = User(
        id=uuid4(),
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        tenant_id=tenant_id,
        is_superuser=False,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Assign default VIEWER role
    q_role = select(Role).where(Role.name == "VIEWER", Role.tenant_id == tenant_id)
    result = await db.execute(q_role)
    viewer_role = result.scalar_one_or_none()

    if viewer_role:
        db.add(
            UserRole(user_id=new_user.id, role_id=viewer_role.id, tenant_id=tenant_id)
        )
        await db.commit()

    return new_user


# ---------------------------------------------------------------------------
# 📋 List Users
# ---------------------------------------------------------------------------
async def list_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    tenant_id: Optional[str] = None,
    include_inactive: bool = False,
) -> Tuple[int, list[User]]:
    """Return paginated list of users under a tenant (including child tenants)."""
    tenant_ids = [tenant_id] if tenant_id else []

    if tenant_id:
        query = text("""
            WITH RECURSIVE child_tenants AS (
                SELECT id FROM tenants WHERE parent_id = :parent_id
                UNION
                SELECT t.id FROM tenants t
                INNER JOIN child_tenants ct ON t.parent_id = ct.id
            )
            SELECT id FROM child_tenants
        """)
        result = await db.execute(query, {"parent_id": tenant_id})
        tenant_ids.extend([row[0] for row in result.fetchall()])

    # Build WHERE clause
    base_condition = "tenant_id = ANY(:tenant_ids)"
    if not include_inactive:
        base_condition += " AND is_active = TRUE"

    # Count total
    total_query = text(f"SELECT COUNT(*) FROM users WHERE {base_condition}")
    total_result = await db.execute(total_query, {"tenant_ids": tenant_ids})
    total = total_result.scalar() or 0

    # Fetch users
    users_query = text(f"""
        SELECT * FROM users
        WHERE {base_condition}
        ORDER BY created_at DESC
        OFFSET :skip LIMIT :limit
    """)
    users_result = await db.execute(
        users_query,
        {"tenant_ids": tenant_ids, "skip": skip, "limit": limit},
    )
    users = [User(**dict(row)) for row in users_result.mappings().all()]

    return total, users


# ---------------------------------------------------------------------------
# 🔍 User Lookup
# ---------------------------------------------------------------------------
async def get_user_by_email(
    db: AsyncSession,
    email: str,
    tenant_id: Optional[UUID] = None,
) -> Optional[User]:
    """Retrieve a user by email, optionally filtered by tenant."""
    query = select(User).where(User.email == email)
    if tenant_id:
        query = query.where(User.tenant_id == tenant_id)
    result = await db.execute(query)
    return result.scalars().first()


# ---------------------------------------------------------------------------
# 🔐 Authentication Logic
# ---------------------------------------------------------------------------
async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> Optional[User]:
    """Authenticate a user by email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=403, detail="Account is inactive.")
    return user


# ---------------------------------------------------------------------------
# 🎟️ Token Helpers
# ---------------------------------------------------------------------------
def create_tokens_for_user(user: User, roles: List[str]) -> dict:
    """Generate access and refresh tokens for a user."""
    access_token = create_access_token(
        user_id=user.id, tenant_id=user.tenant_id, roles=roles
    )
    refresh_token = create_refresh_token(user_id=user.id, tenant_id=user.tenant_id)

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "tokenType": "Bearer",
        "expiresIn": 3600,
        "user_id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "roles": roles,
    }
