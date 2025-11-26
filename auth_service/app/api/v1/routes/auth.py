# auth_service/app/api/v1/routes/auth.py
"""Authentication routes for login, token refresh, and logout."""

import uuid
from datetime import datetime
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError
from shared_service.app.core.config import settings
from shared_service.app.utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.app.crud.token_blacklist import token_blacklist_crud
from auth_service.app.db.session import get_db
from auth_service.app.schemas.auth import LoginRequest, RefreshRequest

USER_SERVICE_URL = settings.USER_SERVICE_URL
AUTH_ISSUER = settings.AUTH_ISSUER
AUTH_AUDIENCE = settings.AUTH_AUDIENCE

router = APIRouter(prefix="/auth", tags=["auth"])


# -------------------------
# Helper
# -------------------------
def _calculate_expiration(payload: dict) -> tuple[int, int]:
    """Convert exp → UNIX timestamp + calculate expires_in."""
    now_ts = int(datetime.utcnow().timestamp())
    exp = (
        int(payload["exp"].timestamp())
        if hasattr(payload["exp"], "timestamp")
        else int(payload["exp"])
    )
    return exp, max(exp - now_ts, 0)


# -------------------------
# LOGIN
# -------------------------
@router.post("/login")
async def login(request: Request, payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> Any:
    """Authenticate user and return JWT tokens."""

    # Use non-blocking httpx instead of requests
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            response = await client.post(
                f"{USER_SERVICE_URL}/users/verify",
                json={"email": payload.email, "password": payload.password},
            )
            response.raise_for_status()
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="User service unavailable",
            )

    user_data = response.json().get("result", {})
    if not user_data:
        raise HTTPException(401, "Invalid email or password")

    user_id = str(user_data.get("id"))
    roles = sorted(user_data.get("roles", []))
    permissions = sorted(user_data.get("permissions", []))
    tenant_id = user_data.get("tenant_id")

    # Generate JWT access + refresh tokens
    access_token, access_payload = create_access_token(
        sub=user_id,
        iss=AUTH_ISSUER,
        aud=AUTH_AUDIENCE,
        roles=roles,
        permissions=permissions,
        tenant_id=tenant_id,
        return_payload=True,
    )
    refresh_token, refresh_payload = create_refresh_token(sub=user_id, return_payload=True)

    access_exp, access_expires_in = _calculate_expiration(access_payload)
    refresh_exp, refresh_expires_in = _calculate_expiration(refresh_payload)

    return {
        "trace_id": str(uuid.uuid4()),
        "correlation_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "success": True,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "roles": roles,
        "permissions": permissions,
        "data": {
            "sub": user_id,
            "iss": AUTH_ISSUER,
            "aud": AUTH_AUDIENCE,
            "jti": access_payload["jti"],
            "iat": int(
                access_payload["iat"].timestamp()
                if hasattr(access_payload["iat"], "timestamp")
                else access_payload["iat"]
            ),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "access_exp": access_exp,
            "refresh_exp": refresh_exp,
            "access_expires_in": access_expires_in,
            "refresh_expires_in": refresh_expires_in,
            "token_type": "bearer",
        },
        "error": None,
        "meta": {"api_version": "v1", "request_path": str(request.url.path)},
    }


# -------------------------
# REFRESH TOKEN
# -------------------------
@router.post("/refresh")
async def refresh_token(
    request: Request, payload: RefreshRequest, db: AsyncSession = Depends(get_db)
) -> Any:
    """Refresh an access token using a valid refresh token."""

    try:
        token_payload = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")

    jti = token_payload.get("jti", str(uuid.uuid4()))

    # Async blacklist check
    is_blacklisted = await token_blacklist_crud.is_blacklisted(db, jti)
    if is_blacklisted:
        raise HTTPException(401, f"Refresh token with jti={jti} is blacklisted")

    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(401, "Invalid token payload")

    roles = token_payload.get("roles", [])
    permissions = token_payload.get("permissions", [])
    tenant_id = token_payload.get("tenant_id")

    access_token, access_payload = create_access_token(
        sub=user_id,
        iss=AUTH_ISSUER,
        aud=AUTH_AUDIENCE,
        roles=roles,
        permissions=permissions,
        tenant_id=tenant_id,
        return_payload=True,
    )
    new_refresh_token, refresh_payload = create_refresh_token(sub=user_id, return_payload=True)

    access_exp, access_expires_in = _calculate_expiration(access_payload)
    refresh_exp, refresh_expires_in = _calculate_expiration(refresh_payload)

    return {
        "trace_id": str(uuid.uuid4()),
        "correlation_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "success": True,
        "user_id": user_id,
        "tenant_id": tenant_id,
        "roles": roles,
        "permissions": permissions,
        "data": {
            "sub": user_id,
            "iss": AUTH_ISSUER,
            "aud": AUTH_AUDIENCE,
            "jti": jti,
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "access_exp": access_exp,
            "refresh_exp": refresh_exp,
            "access_expires_in": access_expires_in,
            "refresh_expires_in": refresh_expires_in,
            "token_type": "bearer",
        },
        "error": None,
        "meta": {"api_version": "v1", "request_path": str(request.url.path)},
    }


# -------------------------
# LOGOUT — blacklist refresh token
# -------------------------
@router.post("/logout")
async def logout(
    request: Request, payload: RefreshRequest, db: AsyncSession = Depends(get_db)
) -> Any:
    """Blacklist a refresh token."""

    try:
        token_payload = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(401, "Invalid token")

    jti = token_payload.get("jti", str(uuid.uuid4()))

    try:
        await token_blacklist_crud.add(db, jti)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(400, f"Token with jti={jti} is already blacklisted")

    return {
        "trace_id": str(uuid.uuid4()),
        "correlation_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "success": True,
        "user_id": token_payload.get("sub"),
        "tenant_id": token_payload.get("tenant_id"),
        "roles": token_payload.get("roles", []),
        "permissions": token_payload.get("permissions", []),
        "data": {"detail": "Successfully logged out"},
        "error": None,
        "meta": {"api_version": "v1", "request_path": str(request.url.path)},
    }
