# ima_service/app/api/v1/routes/auth.py
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import APIRouter, Depends, Header, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.core.audit_adapter import audit_logger, current_user_id, current_tenant_id
from app.db.session import get_db
from app.models.auth_tokens import AuthToken
from app.schemas.auth_tokens import TokenData, TokenResponse, TokenUser
from app.services.auth_service import AuthService
from app.services.crud_service import CRUDService
from app.services.rbac_service import RBACService
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.dependency.auth import get_current_user
from app.core.security import (
    validate_refresh_token,
    revoke_token,
    create_access_token,
    create_refresh_token,
)

# -------------------------------
# Setup
# -------------------------------
settings = get_settings()
router = APIRouter()
security_scheme = HTTPBearer()


# -------------------------------
# Request Models
# -------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# -------------------------------
# Login Route
# -------------------------------
@router.post("/login")
async def login(
    login_req: LoginRequest,
    db: AsyncSession = Depends(get_db),
    x_tenant_id: Optional[str] = Header(None, alias="x-tenant-id"),
) -> Dict:
    # Setup services
    role_service = RoleService(db=db, tenant_id=x_tenant_id)
    permission_crud = CRUDService(db=db, tenant_id=x_tenant_id)
    rbac_service = RBACService(role_service=role_service, permission_crud=permission_crud)
    user_service = UserService(db=db, rbac_service=rbac_service, tenant_id=x_tenant_id)
    auth_service = AuthService(user_service=user_service, db=db, tenant_id=x_tenant_id)

    # Login and set ContextVars inside AuthService
    tokens = await auth_service.login(email=login_req.email, password=login_req.password)
    return tokens


# -------------------------------
# Refresh Token Route
# -------------------------------
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    x_tenant_id: str = Header(..., alias="x-tenant-id"),
    openapi_extra={"security": [{"BearerAuth": []}]},
):
    refresh_token_str = payload.refresh_token
    if not refresh_token_str:
        raise BadRequestException("Refresh token required")

    # Validate refresh token
    token_record = await validate_refresh_token(
        token_str=refresh_token_str, db=db, tenant_id=x_tenant_id
    )

    user_id = token_record.user_id
    tenant_id = token_record.tenant_id

    # Setup services
    role_service = RoleService(db=db, tenant_id=tenant_id)
    permission_crud = CRUDService(db=db, tenant_id=tenant_id)
    rbac_service = RBACService(role_service=role_service, permission_crud=permission_crud)
    user_service = UserService(db=db, rbac_service=rbac_service, tenant_id=tenant_id)
    user = await user_service.get_by_id(user_id)
    if not user:
        raise NotFoundException("User not found")

    user_roles = await role_service.get_user_roles(user_id)
    user_permissions = await role_service.get_user_permissions(user_id)

    # Issue new tokens
    access_token = create_access_token(user_id=user_id, tenant_id=tenant_id, roles=user_roles)
    await revoke_token(token_record, db)  # revoke old refresh token
    refresh_token_new = create_refresh_token(user_id=user_id, tenant_id=tenant_id)
    db.add(refresh_token_new)
    await db.commit()
    await db.refresh(refresh_token_new)
    refresh_token_new.last_used_at = datetime.now(timezone.utc)
    await db.commit()

    token_user = TokenUser(
        id=user.id,
        email=user.email,
        full_name=getattr(user, "full_name", None),
        tenant_id=tenant_id,
        roles=user_roles,
        permissions=user_permissions,
    )
    token_data = TokenData(
        access_token=access_token.token,
        refresh_token=refresh_token_new.token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=token_user,
    )

    # Audit log with explicit actor_id/tenant_id
    await audit_logger.log(
        action="refresh_token",
        resource="auth_token",
        status=200,
        actor_id=str(user_id),
        tenant_id=tenant_id,
        meta={"new_access_jti": access_token.jti, "new_refresh_jti": refresh_token_new.jti},
    )

    return TokenResponse(
        data=token_data,
        meta={
            "request_id": f"req_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# -------------------------------
# Logout Route
# -------------------------------
@router.post(
    "/logout",
    summary="Logout API: revoke refresh token(s)",
    description=(
        "Only authenticated users can logout.\n"
        "Provide Authorization header (Bearer access token).\n"
        "If `refresh_token` is provided, revoke only that token.\n"
        "Otherwise revoke all refresh tokens for the current user."
    ),
    response_model=dict,
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def logout(
    refresh_token: Optional[str] = Query(None, description="Refresh token to revoke"),
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user:
        raise UnauthorizedException("User not authenticated")

    auth_service = AuthService(user_service=None, db=db)

    revoked_count = 0
    if refresh_token:
        revoked_count = await auth_service.revoke_single_token(refresh_token, db, current_user.id)
    else:
        revoked_count = await auth_service.revoke_all_tokens_for_user(
            user_id=current_user.id,
            db=db,
            tenant_id=current_user.tenant_id,
        )

    # Audit log with explicit IDs
    await audit_logger.log(
        action="logout",
        resource="auth_token",
        status=200,
        actor_id=current_user.id,
        tenant_id=current_user.tenant_id,
        meta={"revoked_count": revoked_count},
    )

    return {"message": "Logged out successfully", "revoked_count": revoked_count}
