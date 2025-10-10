from __future__ import annotations
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.db import get_db
from app.models.user import User
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    # 🔹 Lazy import to break circular import
    from app.services.user_service import UserService

    payload = decode_token(token)
    user_id: Optional[str] = payload.get("sub")
    tenant_id: Optional[str] = payload.get("tenant_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user_service = UserService(db, tenant_id=tenant_id)
    user = await user_service.get_by_id(user_id)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )

    return user


def require_roles(required_roles: List[str]):
    """
    Dependency to ensure current_user has at least one of the required roles.
    Usage:
        @router.get("/admin")
        async def admin_route(current_user: User = Depends(require_roles(["admin"]))):
            ...
    """

    async def checker(current_user: User = Depends(get_current_user)):
        if not hasattr(current_user, "roles") or not any(
            role in current_user.roles for role in required_roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return checker
