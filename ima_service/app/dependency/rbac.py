# ima_service/app/dependency/rbac.py
"""RBAC (Role-Based Access Control) dependencies for FastAPI routes."""

from typing import List
from fastapi import Depends, HTTPException, status

from app.dependency.auth import get_current_user  # type:ignore[import-not-found]
from app.models.user import User  # type:ignore[import-not-found]


def require_roles(required_roles: List[str]):
    """Dependency factory to enforce user roles."""

    async def dependency(user: User = Depends(get_current_user)):
        user_roles = [role.name for role in user.roles]
        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden"
            )
        return user

    return dependency
