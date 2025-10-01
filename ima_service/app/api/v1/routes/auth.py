"""
Authentication endpoints: login, refresh, logout.
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from ima_service.app.api.v1.docs.auth_docs import LOGIN, LOGOUT, REFRESH_TOKEN
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import get_settings
from app.crud.user_basic import get_user_by_email
from app.schemas.auth import LoginAPIResponse, LoginRequest, Token, TokenRefresh
from app.utils.security import verify_password
from app.utils.token import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


# ----------------------
# 1️⃣ Login
# ----------------------
@router.post(
    "/login",
    response_model=LoginAPIResponse,
    status_code=status.HTTP_200_OK,
    summary=LOGIN["summary"],
    description=LOGIN["description"],
)
async def login(
    login_data: LoginRequest, db: AsyncSession = Depends(get_db)
) -> LoginAPIResponse:
    """
    Authenticate a user with email and password and return access & refresh tokens.

    Parameters
    ----------
    login_data : LoginRequest
        User login details (email and password).
    db : AsyncSession, optional
        SQLAlchemy async session.

    Returns
    -------
    LoginAPIResponse
        Standardized response containing access & refresh tokens.

    Raises
    ------
    HTTPException
        401 Unauthorized if credentials are invalid or user is inactive.
    """
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


# ----------------------
# 2️⃣ Refresh Token
# ----------------------
@router.post(
    "/refresh",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary=REFRESH_TOKEN["summary"],
    description=REFRESH_TOKEN["description"],
)
async def refresh_token(data: TokenRefresh) -> Dict[str, Any]:
    """
    Exchange a valid refresh token for a new access token.

    Parameters
    ----------
    data : TokenRefresh
        Refresh token payload.

    Returns
    -------
    dict
        Dictionary containing new access and refresh tokens, token type, and expiry.

    Raises
    ------
    HTTPException
        400 Bad Request if the refresh token is invalid.
    """
    payload = decode_token(data.refreshToken)
    if payload.get("type") != "refresh" or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token"
        )

    user_id = payload["sub"]
    access_token = create_access_token({"sub": str(user_id), "type": "access"})
    _refresh_token = create_refresh_token({"sub": str(user_id), "type": "refresh"})

    return {
        "accessToken": access_token,
        "refreshToken": _refresh_token,
        "tokenType": "bearer",
        "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


# ----------------------
# 3️⃣ Logout
# ----------------------
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary=LOGOUT["summary"],
    description=LOGOUT["description"],
)
async def logout() -> Dict[str, str]:
    """
    Logout a user from the system (placeholder).

    Returns
    -------
    dict
        Message indicating logout success.

    Notes
    -----
    Implement token revocation/blacklisting if needed for security.
    """
    return {"detail": "Logout successful"}
