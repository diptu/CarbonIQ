# app/api/v1/routes/auth_router.py

from fastapi import APIRouter, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.core.config import get_settings
from app.db.session import get_db
from app.services.user_service import get_user_by_email, verify_password
from app.core.token import create_access_token, create_refresh_token
from app.schemas.auth import LoginResponse, TokenDetails

router = APIRouter()
settings = get_settings()


# app/api/v1/routes/auth_router.py
from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID

from app.core.config import get_settings
from app.db.session import get_db
from app.services.user_service import authenticate_user
from app.core.token import create_access_token, create_refresh_token
from app.schemas.auth import LoginResponse, TokenDetails

router = APIRouter()
settings = get_settings()


@router.post("/login", response_model=LoginResponse)
async def login(
    email: str = Form(..., description="Your email address"),
    password: str = Form(..., description="Your password"),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT access + refresh tokens.
    Automatically resolves tenant_id from the user record.
    """

    # 1️⃣ Authenticate user
    user = await authenticate_user(db, email, password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=403, detail="Inactive user. Contact admin.")

    # 2️⃣ Resolve tenant_id automatically from user
    tenant_id_to_use: Optional[str] = getattr(user, "tenant_id", None)

    # 3️⃣ Get user roles (for future RBAC)
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

    return LoginResponse(
        statusCode=200,
        msg="Login successful",
        details=details.model_dump(),  # ✅ ensure dict for Pydantic validation
    )
