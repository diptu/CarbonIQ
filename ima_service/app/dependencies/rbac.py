# app/dependencies/rbac.py
"""Role & permission dependency utilities for FastAPI endpoints."""

from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
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

    def decorator(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db_session),
    ):
        if current_user.is_superuser:
            return current_user  # bypass all checks

        # Fetch all roles for this user in their tenant
        user_roles = (
            db.query(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .filter(
                UserRole.user_id == current_user.id,
                UserRole.tenant_id == current_user.tenant_id,
            )
            .all()
        )
        if not user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No roles assigned"
            )

        # -----------------
        # Role check
        # -----------------
        has_role = False
        if required_roles:
            max_user_level = max(role.level for role in user_roles)
            required_levels = (
                db.query(Role.level).filter(Role.name.in_(required_roles)).all()
            )
            required_level = (
                max([lvl[0] for lvl in required_levels]) if required_levels else 0
            )
            has_role = max_user_level >= required_level

        # -----------------
        # Permission check
        # -----------------
        has_permission = False
        if required_permissions:
            permission_names = set()
            for role in user_roles:
                perms = (
                    db.query(Permission.name)
                    .join(RolePermission, Permission.id == RolePermission.permission_id)
                    .filter(RolePermission.role_id == role.id)
                    .all()
                )
                permission_names.update([p[0] for p in perms])
            has_permission = all(p in permission_names for p in required_permissions)

        if not (has_role or has_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient roles or permissions",
            )

        return current_user

    return decorator


def require_permissions(required_permissions: List[str]):
    """Shortcut decorator for requiring only permissions."""
    return require_roles_or_permissions(required_permissions=required_permissions)


def require_roles(required_roles: List[str]):
    """Shortcut decorator for requiring only roles."""
    return require_roles_or_permissions(required_roles=required_roles)
