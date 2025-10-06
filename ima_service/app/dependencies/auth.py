# app/dependency/auth.py
from typing import List
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

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
    """
    Extract current user from JWT token.
    Skips actual DB check if called during OpenAPI generation (Swagger UI)
    """
    # Skip token check for OpenAPI docs
    import sys

    if "pydantic_openapi" in sys.modules:
        return None  # dummy user for OpenAPI generation

    try:
        # Decode JWT with full validation
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,  # Must match create_access_token
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )
        user_id = UUID(payload["user_id"])
        tenant_id = UUID(payload["tenant_id"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == tenant_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def require_permissions(required_permissions: List[str]):
    async def decorator(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session),
    ):
        # Skip permissions check if called during OpenAPI generation
        import sys

        if current_user is None or "pydantic_openapi" in sys.modules:
            return None

        if current_user.is_superuser:
            return current_user

        result = await db.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(
                UserRole.user_id == current_user.id,
                UserRole.tenant_id == current_user.tenant_id,
            )
        )
        user_roles = result.scalars().all()

        permission_names = set()
        for role in user_roles:
            res = await db.execute(
                select(Permission.name)
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .where(RolePermission.role_id == role.id)
            )
            permission_names.update([p[0] for p in res.all()])

        missing = [p for p in required_permissions if p not in permission_names]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {missing}",
            )

        return current_user

    return decorator
