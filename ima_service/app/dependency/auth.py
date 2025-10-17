# ima_service/app/dependency/auth.py
from typing import Tuple
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.exceptions import UnauthorizedException
from app.models.user import User
from .db import get_async_db

# OAuth2 scheme for Swagger UI & automatic Bearer token detection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_and_tenant(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> Tuple[User, str]:
    """
    Validate JWT, fetch User, and extract Tenant ID.

    Raises UnauthorizedException if token is missing, invalid, expired, or user inactive.
    """
    payload = security.verify_token(token)
    if not payload:
        raise UnauthorizedException("Token is invalid or expired.")

    user_id = payload.get("user_id")
    tenant_id = payload.get("tenant_id")
    token_type = payload.get("type")

    if token_type != "access" or not all([user_id, tenant_id]):
        raise UnauthorizedException("Invalid token claims or not an access token.")

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive.")

    return user, tenant_id


async def get_current_user(
    data: Tuple[User, str] = Depends(get_current_user_and_tenant),
) -> User:
    """Return the authenticated User."""
    return data[0]


async def get_current_tenant_id(
    data: Tuple[User, str] = Depends(get_current_user_and_tenant),
) -> str:
    """Return the authenticated Tenant ID."""
    return data[1]
