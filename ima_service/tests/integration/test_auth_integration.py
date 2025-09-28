"""Authentication endpoints for login, refresh, and logout."""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from ima_service.app.api.deps import get_db
from ima_service.app.crud.user_basic import get_user_by_email
from ima_service.app.schemas.auth import Token, TokenRefresh
from ima_service.app.utils.security import verify_password
from ima_service.app.utils.token import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from ima_service.app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Authenticate user and issue access + refresh tokens.
    """
    settings = get_settings()

    user = await get_user_by_email(db, email=form_data.username)

    if (
        not user
        or not verify_password(
            form_data.password,
            user.hashed_password,  # type: ignore[arg-type]
        )
        or not user.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token({"sub": str(user.id), "type": "access"})
    refresh_jwt = create_refresh_token({"sub": str(user.id), "type": "refresh"})

    return {
        "access_token": access_token,
        "refresh_token": refresh_jwt,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(data: TokenRefresh) -> Dict[str, Any]:
    """
    Exchange refresh token for a new access token.
    """
    settings = get_settings()

    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token",
        )

    access_token = create_access_token({"sub": str(user_id), "type": "access"})
    refresh_jwt = create_refresh_token({"sub": str(user_id), "type": "refresh"})

    return {
        "access_token": access_token,
        "refresh_token": refresh_jwt,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout")
async def logout() -> Dict[str, str]:
    """
    Logout user. (Optional: implement token blacklist with Redis.)
    """
    return {"detail": "Logout successful"}
