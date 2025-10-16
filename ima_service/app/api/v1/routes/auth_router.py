from __future__ import annotations
from typing import Dict, Optional
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone
import uuid

from app.db.session import get_db
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.services.rbac_service import RBACService
from app.services.crud_service import CRUDService
from app.services.auth_service import AuthService

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
@router.post("/refresh")
async def refresh_token(
    req: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    x_tenant_id: Optional[str] = Header(None, alias="x-tenant-id"),
) -> Dict:
    role_service = RoleService(db=db, tenant_id=x_tenant_id)
    permission_crud = CRUDService(db=db, tenant_id=x_tenant_id)
    rbac_service = RBACService(role_service=role_service, permission_crud=permission_crud)
    user_service = UserService(db=db, rbac_service=rbac_service, tenant_id=x_tenant_id)
    auth_service = AuthService(user_service=user_service, db=db, tenant_id=x_tenant_id)

    try:
        payload = await auth_service.refresh(req.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return payload
