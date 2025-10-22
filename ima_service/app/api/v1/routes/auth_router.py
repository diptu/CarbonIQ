# ima_service/app/api/v1/routes/auth.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional, Tuple

from fastapi import APIRouter, Depends, Header, Security, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from app.core.audit_adapter import audit_logger
from app.db.session import get_db
from app.schemas.auth_tokens import TokenData, TokenUser
from app.schemas.auth import LoginRequest, RefreshRequest, APIResponse
from app.services.auth_service import AuthService
from app.services.crud_service import CRUDService
from app.services.rbac_service import RBACService
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.dependency.auth import get_current_user
from app.core.security import (
    validate_refresh_token,
    create_access_token,
    create_refresh_token,
    revoke_token,
)

settings = get_settings()
router = APIRouter()
security_scheme = HTTPBearer()


# -------------------------------
# Helper to build services
# -------------------------------
def build_services(
    db: AsyncSession, tenant_id: str
) -> Tuple[RoleService, UserService, AuthService]:
    """
    Build service instances for given tenant.

    Parameters
    ----------
    db : AsyncSession
        Database session.
    tenant_id : str
        Tenant identifier.

    Returns
    -------
    role_service, user_service, auth_service
        Initialized service instances.
    """
    role_service = RoleService(db=db, tenant_id=tenant_id)
    crud = CRUDService(db=db, tenant_id=tenant_id)
    rbac = RBACService(role_service=role_service, permission_crud=crud)
    user_service = UserService(db=db, rbac_service=rbac, tenant_id=tenant_id)
    auth_service = AuthService(user_service=user_service, db=db, tenant_id=tenant_id)
    return role_service, user_service, auth_service


# -------------------------------
# Login
# -------------------------------
@router.post("/login", response_model=APIResponse, summary="User login")
async def login(
    login_req: LoginRequest,
    db: AsyncSession = Depends(get_db),
    x_tenant_id: Optional[str] = Header(None, alias="x-tenant-id"),
) -> APIResponse:
    """
    Login user. Super-admins can omit tenant header.

    Parameters
    ----------
    login_req : LoginRequest
        Email and password.
    db : AsyncSession
        Database session.
    x_tenant_id : Optional[str]
        Tenant header.

    Returns
    -------
    APIResponse
        Access & refresh tokens with user info.
    """
    _, _, auth_service = build_services(db, x_tenant_id or "")
    tokens = await auth_service.login(email=login_req.email, password=login_req.password)
    return APIResponse.success(data=tokens, message="Login successful")


# -------------------------------
# Refresh token
# -------------------------------
@router.post("/refresh", response_model=APIResponse, summary="Refresh access token")
async def refresh_token(
    payload: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    x_tenant_id: str = Header(..., alias="x-tenant-id"),
) -> APIResponse:
    """
    Refresh access token using a valid refresh token.
    """
    if not payload.refresh_token:
        raise BadRequestException("Refresh token required")

    # Validate refresh token (signature, tenant, revocation)
    token_record = await validate_refresh_token(payload.refresh_token, db, tenant_id=x_tenant_id)
    if not token_record or token_record.revoked:
        raise UnauthorizedException("Invalid or revoked refresh token")

    user_id, tenant_id = token_record.user_id, token_record.tenant_id

    # Build services
    role_service, user_service, auth_service = build_services(db, tenant_id)
    user = await user_service.get_by_id(user_id)
    if not user:
        raise NotFoundException("User not found")

    # Rotate refresh token
    new_refresh_token = await auth_service.rotate_refresh_token(token_record, db)

    # Create new access token
    roles, permissions = (
        await role_service.get_user_roles(user_id),
        await role_service.get_user_permissions(user_id),
    )
    access_token = create_access_token(user_id=user_id, tenant_id=tenant_id, roles=roles)

    # Build token user
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
        refresh_token=new_refresh_token.token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=token_user,
    )

    # Audit log
    await audit_logger.log(
        action="refresh_token",
        resource="auth_token",
        status=200,
        actor_id=str(user_id),
        tenant_id=tenant_id,
        meta={
            "old_refresh_jti": token_record.jti,
            "new_access_jti": access_token.jti,
            "new_refresh_jti": new_refresh_token.jti,
        },
    )

    return APIResponse.success(data=token_data.dict())


# -------------------------------
# Logout
# -------------------------------
@router.post("/logout", response_model=APIResponse, summary="Logout user")
async def logout(
    refresh_token: Optional[str] = Query(None),
    credentials: HTTPAuthorizationCredentials = Security(security_scheme),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    """
    Logout user by revoking refresh tokens.

    Parameters
    ----------
    refresh_token : Optional[str]
        Single token to revoke.
    credentials : HTTPAuthorizationCredentials
        Access token credentials.
    current_user : User
        Currently authenticated user.
    db : AsyncSession
        Database session.

    Returns
    -------
    APIResponse
        Revocation result with count.
    """
    auth_service = AuthService(user_service=None, db=db)

    # Determine user context
    user_id = None
    tenant_id = None
    if current_user:
        user_id = current_user.id
        tenant_id = current_user.tenant_id
    elif refresh_token:
        # Extract user from refresh token if access token is missing
        token_data = await auth_service.validate_refresh_token(refresh_token, db)
        user_id = token_data.user_id
        tenant_id = token_data.tenant_id
    else:
        raise UnauthorizedException("User not authenticated and no refresh token provided")

    # Revoke tokens
    if refresh_token:
        revoked_count = await auth_service.revoke_single_token(refresh_token, db, user_id)
    else:
        revoked_count = await auth_service.revoke_all_tokens_for_user(user_id, db, tenant_id)

    # Audit log
    await audit_logger.log(
        action="logout",
        resource="auth_token",
        status=200,
        actor_id=user_id,
        tenant_id=tenant_id,
        meta={"revoked_count": revoked_count},
    )

    return APIResponse.success(
        data={"message": "Logged out successfully", "revoked_count": revoked_count}
    )
