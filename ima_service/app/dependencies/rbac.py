# app/dependencies/rbac.py
"""RBAC enforcement dependency for FastAPI endpoints and services."""

from __future__ import annotations
from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models.permission import Permission
from app.models.role import Role
from app.models.user_roles import UserRole


# -------------------------
# Service / Sync usage
# -------------------------
def check_permission(
    db: Session,
    user_id: str,
    permission_name: str,
    tenant_id: str | None = None,
) -> bool:
    """Check if a user has a permission (synchronous, service layer)."""
    query = (
        db.query(Permission.name)
        .join(Role, Role.id == Permission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user_id)
    )

    if tenant_id:
        query = query.filter(Permission.tenant_id == tenant_id)

    user_permissions = query.all()
    perm_names = {p[0] for p in user_permissions}

    return permission_name in perm_names


# -------------------------
# FastAPI Dependencies / Async endpoints
# -------------------------
async def require_permissions(
    permissions: List[str],
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> bool:
    """Ensure current user has required permissions (FastAPI endpoint)."""
    user_permissions = (
        db.query(Permission.name)
        .join(Role, Role.id == Permission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == current_user.id)
        .all()
    )
    user_perm_names = {p[0] for p in user_permissions}

    for perm in permissions:
        if perm not in user_perm_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{perm}' required",
            )
    return True


async def require_roles(
    roles: List[str],
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
) -> bool:
    """Ensure current user has required roles (FastAPI endpoint)."""
    user_roles = (
        db.query(Role.name)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == current_user.id)
        .all()
    )
    user_role_names = {r[0] for r in user_roles}

    for role in roles:
        if role not in user_role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required",
            )
    return True
