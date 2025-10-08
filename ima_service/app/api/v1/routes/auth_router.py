# app/api/v1/routes/auth_router.py

from fastapi import APIRouter, Form, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.config import get_settings
from app.db.session import get_db
from app.services.user_service import authenticate_user
from app.core.token import create_access_token, create_refresh_token
from app.schemas.auth import LoginResponse, TokenDetails
from app.services.audit_service import log_event

router = APIRouter()
settings = get_settings()


@router.post("/login", response_model=LoginResponse)
@log_event("LOGIN")  # Audit log every login attempt
async def login(
    email: str = Form(..., description="Your email address"),
    password: str = Form(..., description="Your password"),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT access + refresh tokens.
    Proper HTTP status codes used for RBAC violations.
    """

    # 1️⃣ Authenticate user
    user = await authenticate_user(db, email, password)

    if not user:
        # Invalid credentials
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials."
        )

    if not getattr(user, "is_active", True):
        # User exists but is inactive
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user. Contact admin.",
        )

    # 2️⃣ Resolve tenant_id automatically from user
    tenant_id_to_use: Optional[str] = getattr(user, "tenant_id", None)

    # 3️⃣ Get user roles for RBAC
    roles: List[str] = [r.name for r in getattr(user, "roles", [])]

    # 4️⃣ Create JWT tokens
    token_payload = {"user_id": str(user.id)}
    if tenant_id_to_use:
        token_payload["tenant_id"] = str(tenant_id_to_use)

    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)

    # 5️⃣ Build structured response
    details = TokenDetails(
        accessToken=access_token,
        refreshToken=refresh_token,
        tokenType="bearer",
        expiresIn=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        roles=roles or [],
        tenantId=str(tenant_id_to_use) if tenant_id_to_use else None,
    )

    # ✅ Explicitly pass current_user to decorator for logging
    return LoginResponse(
        statusCode=status.HTTP_200_OK,
        msg="Login successful",
        details=details.model_dump(),
        current_user=user,  # Used by log_event decorator
    )
