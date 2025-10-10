from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.dependencies.db import get_db
from app.services.user_service import UserService
from app.core.logger import audit_logger, error_logger
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.schemas.auth import LoginSchema, TokenSchema
from app.core.exceptions import raise_invalid_credentials, raise_inactive_user
from app.models.user import User
from app.core.config import get_settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()  # make sure this points to your config constants


@router.post("/login", response_model=TokenSchema)
async def login(
    login_data: LoginSchema, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    email = login_data.email
    password = login_data.password

    try:
        user_service = UserService(db=db)
        user: User | None = await user_service.get_by_email(email=email)

        if not user:
            audit_logger.info(
                {"event": "login_failed", "email": email, "reason": "user_not_found"}
            )
            raise_invalid_credentials()

        if not user.is_active:
            audit_logger.info(
                {"event": "login_failed", "email": email, "reason": "inactive_user"}
            )
            raise_inactive_user()

        if not verify_password(password, user.password_hash):
            audit_logger.info(
                {"event": "login_failed", "email": email, "reason": "invalid_password"}
            )
            raise_invalid_credentials()

        # Access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            subject=str(user.id),
            tenant_id=str(user.tenant_id),
            expires_delta=access_token_expires,
        )

        # Refresh token
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = create_refresh_token(
            subject=str(user.id),
            tenant_id=str(user.tenant_id),
            expires_delta=refresh_token_expires,
        )

        audit_logger.info(
            {
                "event": "login_success",
                "user_id": str(user.id),
                "tenant_id": str(user.tenant_id),
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "tenant_id": str(user.tenant_id),
        }

    except HTTPException:
        raise
    except Exception as e:
        error_logger.exception(
            {"event": "login_exception", "email": email, "exception": str(e)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
