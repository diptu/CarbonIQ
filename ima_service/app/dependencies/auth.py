# app/dependency/auth.py
from typing import List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError

from app.core.token import decode_token
from app.db.session import get_db as get_db_session
from app.core.config import get_settings
from app.models.user import User
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.models.user_roles import UserRole

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> User:
    import sys

    if "pydantic_openapi" in sys.modules:
        return None

    try:
        payload = decode_token(token)
        if payload is None:
            raise JWTError("Token verification failed")
        user_id = UUID(payload["user_id"])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def require_permissions(required_permissions: List[str]):
    """
    Dependency decorator to enforce permission checks.
    Skips checks for OpenAPI docs.
    Superusers bypass permission checks.
    """

    async def decorator(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session),
    ):
        import sys

        if current_user is None or "pydantic_openapi" in sys.modules:
            return None

        if getattr(current_user, "is_superuser", False):
            return current_user

        # Get user roles for current tenant
        result = await db.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(
                UserRole.user_id == current_user.id,
                UserRole.tenant_id == current_user.tenant_id,
            )
        )
        user_roles = result.scalars().all()

        # Collect all permissions
        permission_names = set()
        for role in user_roles:
            res = await db.execute(
                select(Permission.name)
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .where(RolePermission.role_id == role.id)
            )
            permission_names.update([p[0] for p in res.all()])

        # Check for missing required permissions
        missing = [p for p in required_permissions if p not in permission_names]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {missing}",
            )

        return current_user

    return decorator
