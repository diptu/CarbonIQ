# app/api/v1/routes/auth_router.py
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.dependencies.db import get_db
from app.services.user_service import UserService
from app.core.logger import audit_logger, error_logger
from app.core.security import create_access_token, verify_password
from app.schemas.auth import LoginSchema, TokenSchema
from app.core.exceptions import raise_invalid_credentials, raise_inactive_user
from app.models.user import User

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/login", response_model=TokenSchema)
async def login(
    login_data: LoginSchema, db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """Tenant-aware login endpoint using LoginSchema."""
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

        # Generate access token (use tenant_id directly)
        access_token = create_access_token(
            subject=str(user.id), tenant_id=str(user.tenant_id)
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
            "refresh_token": "",  # optionally implement refresh token
            "token_type": "bearer",
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
