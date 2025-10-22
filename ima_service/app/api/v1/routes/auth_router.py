# ima_service/app/api/v1/routes/auth.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import APIRouter, Depends, Header, Security, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.core.audit_adapter import audit_logger
from app.core.context import current_trace_id, current_correlation_id
from app.db.session import get_db
from app.schemas.auth_tokens import TokenData, TokenUser
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
from app.schemas.auth import LoginRequest, RefreshRequest, APIResponse

settings = get_settings()
router = APIRouter()
security_scheme = HTTPBearer()


# -------------------------------
# Helper to build services
# -------------------------------
def build_services(db: AsyncSession, tenant_id: str):
    role_service = RoleService(db=db, tenant_id=tenant_id)
    crud = CRUDService(db=db, tenant_id=tenant_id)
    rbac = RBACService(role_service=role_service, permission_crud=crud)
    user_service = UserService(db=db, rbac_service=rbac, tenant_id=tenant_id)
    auth_service = AuthService(user_service=user_service, db=db, tenant_id=tenant_id)
    return role_service, user_service, auth_service


# -------------------------------
# Routes
# -------------------------------
@router.post("/login", response_model=APIResponse, summary="User login")
async def login(
    login_req: LoginRequest,
    db: AsyncSession = Depends(get_db),
    x_tenant_id: str = Header(..., alias="x-tenant-id"),
) -> APIResponse:
    _, _, auth_service = build_services(db, x_tenant_id)
    tokens = await auth_service.login(email=login_req.email, password=login_req.password)
    return APIResponse(data=tokens).model_dump()


@router.post("/refresh", response_model=APIResponse, summary="Refresh access token")
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    x_tenant_id: str = Header(..., alias="x-tenant-id"),
) -> APIResponse:
    if not payload.refresh_token:
        raise BadRequestException("Refresh token required")

    token_record = await validate_refresh_token(payload.refresh_token, db, x_tenant_id)
    user_id, tenant_id = token_record.user_id, token_record.tenant_id

    role_service, user_service, _ = build_services(db, tenant_id)
    user = await user_service.get_by_id(user_id)
    if not user:
        raise NotFoundException("User not found")

    roles, permissions = (
        await role_service.get_user_roles(user_id),
        await role_service.get_user_permissions(user_id),
    )
    access_token = create_access_token(user_id=user_id, tenant_id=tenant_id, roles=roles)
    await revoke_token(token_record, db)
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
        roles=roles,
        permissions=permissions,
    )
    token_data = TokenData(
        access_token=access_token.token,
        refresh_token=refresh_token_new.token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=token_user,
    )

    await audit_logger.log(
        action="refresh_token",
        resource="auth_token",
        status=200,
        actor_id=str(user_id),
        tenant_id=tenant_id,
        meta={"new_access_jti": access_token.jti, "new_refresh_jti": refresh_token_new.jti},
    )

    return APIResponse(data=token_data.dict())


@router.post("/logout", response_model=APIResponse, summary="Logout user")
async def logout(
    refresh_token: Optional[str] = Query(None),
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    if not current_user:
        raise UnauthorizedException("User not authenticated")

    auth_service = AuthService(user_service=None, db=db)
    revoked_count = await (
        auth_service.revoke_single_token(refresh_token, db, current_user.id)
        if refresh_token
        else auth_service.revoke_all_tokens_for_user(current_user.id, db, current_user.tenant_id)
    )

    await audit_logger.log(
        action="logout",
        resource="auth_token",
        status=200,
        actor_id=current_user.id,
        tenant_id=current_user.tenant_id,
        meta={"revoked_count": revoked_count},
    )

    return APIResponse(data={"message": "Logged out successfully", "revoked_count": revoked_count})
