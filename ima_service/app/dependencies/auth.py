# app/dependencies/auth.py
from __future__ import annotations

from typing import List, Optional, Set

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.models.user import User
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def _fetch_effective_role_names(
    db: AsyncSession, user_id: str, tenant_id: Optional[str] = None
) -> List[str]:
    """
    Recursive CTE to get all effective role names for a user.
    Handles global roles (tenant_id IS NULL) and tenant-specific roles.
    """
    sql = text(
        """
        WITH RECURSIVE role_tree AS (
          SELECT r.id, r.name, r.parent_id
          FROM roles r
          JOIN user_roles ur ON ur.role_id = r.id
          WHERE ur.user_id = :user_id
            AND (r.tenant_id IS NULL OR r.tenant_id = :tenant_id)
        UNION
          SELECT p.id, p.name, p.parent_id
          FROM roles p
          JOIN role_tree rt ON rt.parent_id = p.id
          WHERE (p.tenant_id IS NULL OR p.tenant_id = :tenant_id)
        )
        SELECT DISTINCT name FROM role_tree;
        """
    )

    # Cast tenant_id to UUID string if provided, otherwise None
    params = {"user_id": user_id, "tenant_id": tenant_id}

    result = await db.execute(sql, params)
    rows = result.fetchall()
    return [r[0] for r in rows]


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Resolve the current user from JWT and attach:
    - role_names: list[str] (direct role names)
    - effective_roles: set[str] (roles + ancestors via DB)
    """
    from jwt import PyJWTError  # defensive
    from app.services.user_service import UserService

    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id: Optional[str] = payload.get("sub")
    tenant_id: Optional[str] = payload.get("tenant_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    svc = UserService(db=db, tenant_id=tenant_id)
    user = await svc.get_by_id(user_id)

    if not user or not getattr(user, "is_active", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive or missing user",
        )

    # Normalize direct roles: ORM -> list[str] if present
    raw_roles = getattr(user, "roles", []) or []
    direct_role_names = [r.name for r in raw_roles]

    # Fetch effective roles using DB hierarchy (recursive CTE)
    effective_names = await _fetch_effective_role_names(db, str(user.id), tenant_id)

    # Merge direct roles and effective roles
    merged_effective: Set[str] = set(effective_names) | set(direct_role_names)

    # Attach attributes for downstream checks (do NOT overwrite user.roles)
    setattr(user, "role_names", direct_role_names)
    setattr(user, "effective_roles", merged_effective)

    return user


def require_roles(required_roles: List[str]):
    """
    Dependency factory that ensures current_user has one of the
    required roles via DB-driven inheritance (effective_roles).
    """

    async def checker(current_user: User = Depends(get_current_user)):
        # Superuser bypass
        if getattr(current_user, "is_superuser", False):
            return current_user

        effective: Optional[Set[str]] = getattr(current_user, "effective_roles", None)
        if not effective:
            # Defensive fallback to direct roles
            direct = getattr(current_user, "role_names", []) or []
            effective = set(direct)

        if not any(r in effective for r in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return current_user

    return checker
