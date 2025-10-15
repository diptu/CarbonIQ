# ima_service/app/dependency/auth.py
from typing import Annotated, Tuple
from fastapi import Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.exceptions import UnauthorizedException
from app.models.user import User
from .db import get_async_db


async def get_current_user_and_tenant(
    token: Annotated[str, Header(alias="Authorization")],
    db: Annotated[AsyncSession, Depends(get_async_db)],
) -> Tuple[User, str]:
    """Validate JWT, fetch User, and extract Tenant ID."""
    if not token or not token.startswith("Bearer "):
        raise UnauthorizedException("Missing or malformed Authorization header.")

    token_value = token.split(" ", 1)[1]
    payload = security.verify_token(token_value)
    if not payload:
        raise UnauthorizedException("Token is invalid or expired.")

    user_id, tenant_id, token_type = (
        payload.get("user_id"),
        payload.get("tenant_id"),
        payload.get("type"),
    )
    if token_type != "access" or not all([user_id, tenant_id]):
        raise UnauthorizedException("Invalid token claims or not an access token.")

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise UnauthorizedException("User not found or inactive.")
    return user, tenant_id


async def get_current_user(
    data: Annotated[Tuple[User, str], Depends(get_current_user_and_tenant)],
) -> User:
    """Return the authenticated User."""
    return data[0]


async def get_current_tenant_id(
    data: Annotated[Tuple[User, str], Depends(get_current_user_and_tenant)],
) -> str:
    """Return the authenticated Tenant ID."""
    return data[1]
