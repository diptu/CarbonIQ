# app/dependencies/auth.py
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError

from app.core.security import decode_token
from app.db.session import get_db as get_db_session
from app.core.config import get_settings
from app.models.user import User
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.models.user_roles import UserRole
from app.services.base_service import BaseService

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session),
) -> Optional[User]:
    """
    Extract the current user from JWT token.
    Attaches tenant_id_from_token and roles_from_token.
    Skips verification during OpenAPI generation.
    """
    import sys

    if "pydantic_openapi" in sys.modules:
        return None

    try:
        payload = decode_token(token)
        if payload is None:
            raise JWTError("Token verification failed")
        user_id = UUID(payload["user_id"])
        tenant_id_str = payload.get("tenant_id")
        tenant_id: Optional[UUID] = UUID(tenant_id_str) if tenant_id_str else None
        roles: List[str] = payload.get("roles", [])
    except JWTError as e:
        BaseService.log_action(
            action="token_decoding_failed",
            details={"error": str(e), "token": token},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        BaseService.log_action(
            action="user_not_found", details={"user_id": str(user_id)}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    # Attach tenant_id and roles from token for downstream usage
    user.tenant_id_from_token = tenant_id
    user.roles_from_token = roles

    BaseService.log_action(
        action="user_authenticated", details={"user_id": str(user.id)}
    )
    return user


def require_permissions(required_permissions: List[str]):
    """
    Dependency decorator to enforce permission checks.
    Superusers bypass permission checks.
    Uses roles from JWT token; DB query only for permissions.
    """

    async def decorator(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db_session),
    ) -> User:
        import sys

        if current_user is None or "pydantic_openapi" in sys.modules:
            return None

        if getattr(current_user, "is_superuser", False):
            BaseService.log_action(
                action="superuser_bypass",
                details={"user_id": str(current_user.id)},
            )
            return current_user

        tenant_id = getattr(
            current_user, "tenant_id_from_token", current_user.tenant_id
        )
        token_roles = getattr(current_user, "roles_from_token", [])

        if not token_roles:
            BaseService.log_action(
                action="no_roles_assigned", details={"user_id": str(current_user.id)}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned roles",
            )

        # Collect all permissions for the token roles
        permission_names = set()
        for role_name in token_roles:
            res = await db.execute(
                select(Permission.name)
                .join(RolePermission, Permission.id == RolePermission.permission_id)
                .join(Role, Role.id == RolePermission.role_id)
                .where(Role.name == role_name, Role.tenant_id == tenant_id)
            )
            permission_names.update([p[0] for p in res.all()])

        # Check for missing required permissions
        missing = [p for p in required_permissions if p not in permission_names]
        if missing:
            BaseService.log_action(
                action="permission_denied",
                details={
                    "user_id": str(current_user.id),
                    "missing_permissions": missing,
                    "tenant_id": str(tenant_id),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {missing}",
            )

        BaseService.log_action(
            action="permission_granted",
            details={
                "user_id": str(current_user.id),
                "permissions": required_permissions,
                "tenant_id": str(tenant_id),
            },
        )
        return current_user

    return decorator
