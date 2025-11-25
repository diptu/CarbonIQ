# shared_service/app/core/deps.py
from typing import Callable, List, Optional
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared_service.app.core.config import settings
from shared_service.app.utils.jwt_utils import decode_token
from user_service.app.db.session import get_db
from user_service.app.models.role import Role
from user_service.app.models.user import User
from user_service.app.models.user_role import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ---------------------------------------------------
# Async tenant fetch helper
# ---------------------------------------------------
async def fetch_tenant_info(user_id: str) -> Optional[dict]:
    """
    Calls tenant-service to get tenant_id for the given user_id.
    Fail-soft: returns None if service is unavailable or non-200.
    """
    url = f"{settings.TENANT_SERVICE_URL}/memberships/user/{user_id}"
    try:
        async with httpx.AsyncClient(
            timeout=settings.TENANT_REQUEST_TIMEOUT_SECONDS
        ) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                print(f"[Tenant Fetch] user_id={user_id}, data={data}")
                return data
            print(f"[Tenant Fetch] user_id={user_id}, status_code={resp.status_code}")
            return None
    except httpx.RequestError as e:
        print(f"[Tenant Fetch] user_id={user_id}, error={e}")
        return None


# ---------------------------------------------------
# Async get current user
# ---------------------------------------------------
async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Return current authenticated user and cache it per request.
    Includes cached tenant_id to avoid repeated tenant-service calls.
    Pre-fetches roles and permissions to prevent lazy-loading with async session.
    Attaches first membership info if available.
    """
    if hasattr(request.state, "current_user"):
        return request.state.current_user

    # Decode JWT
    try:
        payload = decode_token(token, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        user_id_str: Optional[str] = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        user_id = UUID(user_id_str)
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc

    # Async fetch user with eager-loaded roles and permissions
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles)
            .selectinload(UserRole.role)
            .selectinload(Role.permissions)
        )
        .where(User.id == user_id)
    )
    user: Optional[User] = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    # Fetch tenant memberships from tenant-service
    tenant_data = await fetch_tenant_info(str(user_id))
    tenant_id = None
    tenant_role = None

    if tenant_data and tenant_data.get("success") and tenant_data.get("result"):
        memberships = tenant_data["result"].get("memberships", [])
        if memberships:
            # pick first active membership if available, else first membership
            membership = next(
                (m for m in memberships if m.get("is_active") == "ACTIVE"),
                memberships[0],
            )
            tenant_id = membership.get("tenant_id")
            tenant_role = membership.get("tenant_role")

    # Attach runtime properties
    request.state.tenant_id = tenant_id
    setattr(user, "tenant_id", tenant_id)
    setattr(user, "tenant_role", tenant_role)

    # Cache combined user object
    request.state.current_user = user
    return user


# ---------------------------------------------------
# Permission checker
# ---------------------------------------------------
def require_permissions(permissions: List[str]) -> Callable[[User], User]:
    """
    Dependency to check if current_user has all required permissions.
    """

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        user_perms = set(current_user.permissions_cached)
        missing = [perm for perm in permissions if perm not in user_perms]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {missing}",
            )
        return current_user

    return checker


# ---------------------------------------------------
# Cached current_user wrapper
# ---------------------------------------------------
async def get_cached_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    """
    Return cached current_user if available; otherwise fetch.
    """
    if hasattr(request.state, "current_user"):
        return request.state.current_user

    user = await get_current_user(request=request, db=db)
    request.state.current_user = user
    return user
