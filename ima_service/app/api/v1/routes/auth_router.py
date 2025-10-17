from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    validate_refresh_token,
    revoke_token,
)
from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.db.session import get_db
from app.models.auth_tokens import AuthToken
from app.schemas.auth_tokens import TokenData, TokenResponse, TokenUser
from app.services.auth_service import AuthService
from app.services.crud_service import CRUDService
from app.services.rbac_service import RBACService
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.db.session import get_db
from app.services.audit_adapter import AuditAdapter
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.core.security import AuthToken
from app.db.session import get_db
from app.services.audit_adapter import AuditAdapter
from app.core.exceptions import UnauthorizedException
from app.services.auth_service import AuthService
from app.dependency.auth import get_current_user


audit_logger = AuditAdapter()
settings = get_settings()
router = APIRouter()


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
    role_service = RoleService(db=db, tenant_id=x_tenant_id)
    permission_crud = CRUDService(db=db, tenant_id=x_tenant_id)
    rbac_service = RBACService(role_service=role_service, permission_crud=permission_crud)
    user_service = UserService(db=db, rbac_service=rbac_service, tenant_id=x_tenant_id)
    auth_service = AuthService(user_service=user_service, db=db, tenant_id=x_tenant_id)

    try:
        tokens = await auth_service.login(email=login_req.email, password=login_req.password)
    except HTTPException as he:
        raise he
    return tokens


# -------------------------------
# Refresh Token Route
# -------------------------------


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    x_tenant_id: str = Header(..., alias="x-tenant-id"),
):
    """
    Exchange a valid refresh token for a new access token.
    Steps:
    1. Validate refresh token (expiration + revocation + tenant ownership)
    2. Revoke old refresh token
    3. Issue new access + refresh token
    """
    refresh_token_str = payload.refresh_token
    if not refresh_token_str:
        raise BadRequestException("Refresh token required")

    # -------------------------
    # 1️⃣ Validate refresh token
    # -------------------------
    token_record = await validate_refresh_token(
        token_str=refresh_token_str, db=db, tenant_id=x_tenant_id
    )

    user_id = token_record.user_id
    tenant_id = token_record.tenant_id

    # -------------------------
    # 2️⃣ Setup RBAC and User services
    # -------------------------
    role_service = RoleService(db=db, tenant_id=tenant_id)
    permission_crud = CRUDService(db=db, tenant_id=tenant_id)
    rbac_service = RBACService(role_service=role_service, permission_crud=permission_crud)
    user_service = UserService(db=db, rbac_service=rbac_service, tenant_id=tenant_id)

    # Fetch user
    user = await user_service.get_by_id(user_id)
    if not user:
        raise NotFoundException("User not found")

    user_roles = await role_service.get_user_roles(user_id)
    user_permissions = await role_service.get_user_permissions(user_id)

    # -------------------------
    # 3️⃣ Issue new access token
    # -------------------------
    new_access_token = create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        roles=user_roles,
    )

    # -------------------------
    # 4️⃣ Revoke old refresh token
    # -------------------------
    await revoke_token(token_record, db)

    # -------------------------
    # 5️⃣ Issue new refresh token
    # -------------------------
    new_refresh_token = create_refresh_token(user_id=user_id, tenant_id=tenant_id)
    db.add(new_refresh_token)
    await db.commit()
    await db.refresh(new_refresh_token)

    # Update last used timestamp
    new_refresh_token.last_used_at = datetime.now(timezone.utc)
    await db.commit()

    # -------------------------
    # 6️⃣ Prepare response
    # -------------------------
    token_user = TokenUser(
        id=user.id,
        email=user.email,
        full_name=getattr(user, "full_name", None),
        tenant_id=tenant_id,
        roles=user_roles,
        permissions=user_permissions,
    )

    token_data = TokenData(
        access_token=new_access_token.token,
        refresh_token=new_refresh_token.token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=token_user,
    )

    # -------------------------
    # 7️⃣ Audit log
    # -------------------------
    await audit_logger.log(
        action="refresh_token",
        resource="auth_token",
        status=200,
        tenant_id=tenant_id,
        actor_id=str(user_id),
        meta={"new_access_jti": new_access_token.jti, "new_refresh_jti": new_refresh_token.jti},
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


@router.post("/logout")
async def logout(
    refresh_token: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout API: revokes user's refresh token(s)
    - If `refresh_token` is provided, revoke only that token
    - Otherwise revoke all refresh tokens for the current user
    """
    if not current_user:
        raise UnauthorizedException("User not authenticated")

    auth_service = AuthService(user_service=None, db=db)  # reuse revoke logic

    revoked_count = 0

    if refresh_token:
        # Revoke single token
        revoked_count = await auth_service.revoke_single_token(refresh_token, db)
    else:
        # Revoke all tokens for user
        revoked_count = await auth_service.revoke_all_tokens_for_user(
            user_id=current_user.id, db=db, tenant_id=current_user.tenant_id
        )

    # Audit log
    await audit_logger.log(
        action="logout",
        resource="auth_token",
        status=200,
        actor_id=current_user.id,
        tenant_id=current_user.tenant_id,
        meta={"revoked_count": revoked_count},
    )

    return {"message": "Logged out successfully", "revoked_count": revoked_count}
