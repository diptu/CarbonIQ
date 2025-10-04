"""Dependency utilities for FastAPI endpoints, including RBAC and JWT."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Awaitable, Callable, Optional

from fastapi import HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import async_session
from app.utils.audit import log_audit_event
from app.utils.cache import cache
from app.utils.jwt_utils import decode_token

settings = get_settings()


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
# RBAC dependency
# -----------------------
def require_roles(*roles: str):
    async def dependency(request: Request) -> dict[str, Any]:
        auth_header: Optional[str] = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, "Missing Authorization header"
            )

        token = auth_header[7:]
        try:
            claims = decode_token(token)
        except Exception as exc:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {exc}"
            )

        user_roles = claims.get("role", [])
        if isinstance(user_roles, str):
            user_roles = [user_roles]

        # --- apply hierarchy ---
        ROLE_HIERARCHY = {
            "TENANT_ADMIN": ["TENANT_ADMIN", "BILLING_ADMIN", "MEMBER", "VIEWER"],
            "BILLING_ADMIN": ["BILLING_ADMIN", "MEMBER", "VIEWER"],
            "MEMBER": ["MEMBER", "VIEWER"],
            "VIEWER": ["VIEWER"],
        }
        effective_roles = set()
        for r in user_roles:
            effective_roles.update(ROLE_HIERARCHY.get(r, []))

        if roles and not any(r in effective_roles for r in roles):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient role")

        claims["roles"] = list(effective_roles)
        return claims

    return dependency
