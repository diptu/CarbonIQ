"""
Authentication endpoints: login, refresh, logout.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.user_basic import get_user_by_email
from app.schemas.auth import Token, TokenRefresh, LoginRequest, LoginAPIResponse
from app.utils.security import verify_password
from app.utils.token import create_access_token, create_refresh_token, decode_token
from app.core.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=LoginAPIResponse)
async def login(
    login_data: LoginRequest, db: AsyncSession = Depends(get_db)
) -> LoginAPIResponse:
    """Authenticate user and return access & refresh tokens."""
    user = await get_user_by_email(db, login_data.email)
    if (
        not user
        or not verify_password(login_data.password, user.hashed_password)
        or not user.is_active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token_data = Token(
        accessToken=create_access_token({"sub": str(user.id), "type": "access"}),
        refreshToken=create_refresh_token({"sub": str(user.id), "type": "refresh"}),
        tokenType="bearer",
        expiresIn=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return LoginAPIResponse(statusCode=200, msg="Login successful", details=token_data)


@router.post("/refresh", response_model=Token)
async def refresh_token(data: TokenRefresh) -> Dict[str, Any]:
    """Exchange refresh token for a new access token."""
    payload = decode_token(data.refreshToken)
    if payload.get("type") != "refresh" or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token"
        )

    user_id = payload["sub"]
    access_token = create_access_token({"sub": str(user_id), "type": "access"})
    refresh_token = create_refresh_token({"sub": str(user_id), "type": "refresh"})

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "tokenType": "bearer",
        "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@router.post("/logout")
async def logout() -> Dict[str, str]:
    """Logout placeholder (implement token revocation if needed)."""
    return {"detail": "Logout successful"}
