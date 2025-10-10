# app/api/v1/routes/auth.py
"""Authentication routes for IMA Service.

Pandas-style docstring
----------------------
Provides login, logout, token refresh, and user activation endpoints.

Features
--------
- Async SQLAlchemy session
- Tenant-aware login
- JWT issuance with access and refresh tokens
- RBAC enforcement scaffolding
- Structured logging of authentication events
"""

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.dependencies.db import get_db
from app.dependencies.rbac import check_permission
from app.services.user_service import UserService
from app.core.logger import app_logger, audit_logger, error_logger
from app.core.security import create_access_token, create_refresh_token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login")
async def login(
    email: str,
    password: str,
    tenant: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Login endpoint for users in a tenant-aware context."""
    try:
        user_service = UserService(db=db, tenant_id=tenant)
        user: User | None = await user_service.get_by_email(email=email)

        if not user:
            audit_logger.info(
                {
                    "event": "login_failed",
                    "email": email,
                    "tenant": tenant,
                    "reason": "user_not_found",
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials"
            )

        if not user.is_active:
            audit_logger.info(
                {
                    "event": "login_failed",
                    "email": email,
                    "tenant": tenant,
                    "reason": "inactive_user",
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
            )

        if not pwd_context.verify(password, user.hashed_password):
            audit_logger.info(
                {
                    "event": "login_failed",
                    "email": email,
                    "tenant": tenant,
                    "reason": "invalid_password",
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # Generate JWT tokens
        access_token = create_access_token(user_id=str(user.id), tenant_id=tenant)
        refresh_token = create_refresh_token(user_id=str(user.id), tenant_id=tenant)

        audit_logger.info(
            {"event": "login_success", "user_id": str(user.id), "tenant": tenant}
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {"id": str(user.id), "email": user.email, "tenant": tenant},
        }

    except HTTPException:
        raise
    except Exception as e:
        error_logger.exception(
            {
                "event": "login_exception",
                "email": email,
                "tenant": tenant,
                "exception": str(e),
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/activate_user/{user_id}")
async def activate_user(
    user_id: str, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Activate a user by ID."""
    try:
        user_service = UserService(db=db)
        user = await user_service.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        await user_service.activate_user(user)
        audit_logger.info({"event": "user_activated", "user_id": user_id})
        return {"status": "success", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        error_logger.exception(
            {
                "event": "activate_user_exception",
                "user_id": user_id,
                "exception": str(e),
            }
        )
        raise HTTPException(status_code=500, detail="Internal server error")
