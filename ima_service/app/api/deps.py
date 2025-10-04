"""Dependency utilities for FastAPI endpoints, including RBAC and JWT."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Optional, Sequence

from fastapi import HTTPException, Request, status, Security, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import async_session
from app.utils.jwt_utils import decode_token
from app.crud import user_basic as crud_user
from app.models.user import User

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# -----------------------
# Database dependency
# -----------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Async database session generator for dependency injection."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# -----------------------
# Current active user dependency
# -----------------------
async def get_current_active_user(
    token: str = Security(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Retrieve the currently authenticated active user from JWT token.
    """
    try:
        payload = decode_token(token)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token"
        )

    user = await crud_user.get_user(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Inactive user")

    return user


# -----------------------
# RBAC dependency
# -----------------------
def require_roles(*roles: str):
    """
    RBAC dependency that ensures the current user has one of the required roles.
    Returns the full User model.
    """

    async def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        # Fetch user roles from DB relationship
        user_roles = [r.name for r in getattr(current_user, "roles", [])]

        # Apply hierarchy
        ROLE_HIERARCHY = {
            "TENANT_ADMIN": ["TENANT_ADMIN", "BILLING_ADMIN", "MEMBER", "VIEWER"],
            "BILLING_ADMIN": ["BILLING_ADMIN", "MEMBER", "VIEWER"],
            "MEMBER": ["MEMBER", "VIEWER"],
            "VIEWER": ["VIEWER"],
        }
        effective_roles = set()
        for r in user_roles:
            effective_roles.update(ROLE_HIERARCHY.get(r, []))

        # Check required roles
        if roles and not any(r in effective_roles for r in roles):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient role")

        return current_user  # always a User model

    return dependency
