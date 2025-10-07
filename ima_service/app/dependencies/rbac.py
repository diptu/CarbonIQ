# app/dependencies/rbac.py
"""Async Role & permission dependency utilities for FastAPI endpoints using DB-backed RBAC."""

from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.models.user import User
from app.models.user_roles import UserRole
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.models.role import Role
from app.dependencies.db import get_db_session
from app.dependencies.auth import get_current_user


def require_roles_or_permissions(
    required_roles: Optional[List[str]] = None,
    required_permissions: Optional[List[str]] = None,
):
    """
    FastAPI dependency decorator to enforce that a user has:
    - At least one of the roles in `required_roles` (hierarchical)
    - OR all permissions in `required_permissions`
    Superuser bypasses all checks. Tenant-aware.
    """

    async def decorator(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session),
    ):
        if current_user.is_superuser:
            return current_user  # bypass all checks

        # -----------------
        # Fetch all roles for this user in their tenant
        # -----------------
        q_roles = (
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == current_user.id)
            .where(UserRole.tenant_id == current_user.tenant_id)
        )
        result = await db.execute(q_roles)
        user_roles: List[Role] = result.scalars().all()

        # ---------- DEBUG ----------
        print("DEBUG: current_user.id =", current_user.id)
        print("DEBUG: current_user.tenant_id =", current_user.tenant_id)
        print("DEBUG: user_roles fetched =", [(r.name, r.level) for r in user_roles])
        # ---------------------------

        if not user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No roles assigned",
            )

        # -----------------
        # Role check
        # -----------------
        has_role = False
        if required_roles:
            # Fetch required role levels from DB
            q_req_levels = select(Role.level).where(Role.name.in_(required_roles))
            req_levels_result = await db.execute(q_req_levels)
            required_levels = [lvl[0] for lvl in req_levels_result.all()]
            required_level = max(required_levels) if required_levels else 0

            max_user_level = max(role.level for role in user_roles)

            # ---------- DEBUG ----------
            print("DEBUG: required_roles =", required_roles)
            print("DEBUG: required_levels fetched =", required_levels)
            print("DEBUG: max_user_level =", max_user_level)
            print("DEBUG: required_level =", required_level)
            # ---------------------------

            has_role = max_user_level >= required_level

        # -----------------
        # Permission check
        # -----------------
        has_permission = False
        if required_permissions:
            permission_names = set()
            for role in user_roles:
                q_perms = (
                    select(Permission.name)
                    .join(RolePermission, Permission.id == RolePermission.permission_id)
                    .where(RolePermission.role_id == role.id)
                )
                perm_result = await db.execute(q_perms)
                permission_names.update([p[0] for p in perm_result.all()])
            # ---------- DEBUG ----------
            print("DEBUG: user permissions =", permission_names)
            # ---------------------------
            has_permission = all(p in permission_names for p in required_permissions)

        # -----------------
        # Final check
        # -----------------
        print("DEBUG: has_role =", has_role, ", has_permission =", has_permission)

        if not (has_role or has_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient roles or permissions",
            )

        return current_user

    return decorator


def require_permissions(required_permissions: List[str]):
    """Shortcut decorator for requiring only permissions."""
    return require_roles_or_permissions(required_permissions=required_permissions)


def require_roles(required_roles: List[str]):
    """Shortcut decorator for requiring only roles."""
    return require_roles_or_permissions(required_roles=required_roles)
