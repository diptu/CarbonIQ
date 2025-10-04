from typing import List

from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud.user_basic import get_user_by_email
from app.crud.user_roles import get_user_roles
from app.utils.security import verify_password
from app.utils.jwt_utils import create_access_token, create_refresh_token
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
async def login(
    email: str = Form(..., description="Your email address"),
    password: str = Form(..., description="Your password"),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT access + refresh tokens.
    Tokens now include 'iss' and 'aud' claims for validation.
    """
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=401, detail="User inactive")

    # Fetch user roles from DB
    roles: List[str] = await get_user_roles(db, str(user.id))

    # Generate JWT tokens with issuer and audience
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "type": "access",
            "role": roles,
        }
    )
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "type": "refresh",
            "role": roles,
        }
    )

    return {
        "statusCode": 200,
        "msg": "Login successful",
        "details": {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "tokenType": "bearer",
            "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "roles": roles,
        },
    }
