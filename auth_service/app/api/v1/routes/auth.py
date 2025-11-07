# auth_service/app/api/v1/routes/auth.py
"""Authentication routes for login, token refresh, and logout."""

import uuid
from datetime import datetime
from typing import Any

import anyio
import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError
from shared_service.app.core.config import settings
from shared_service.app.utils.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth_service.app.crud.token_blacklist import token_blacklist_crud
from auth_service.app.db.session import get_db
from auth_service.app.schemas.auth import LoginRequest, RefreshRequest

USER_SERVICE_URL = settings.USER_SERVICE_URL
AUTH_ISSUER = settings.AUTH_ISSUER
AUTH_AUDIENCE = settings.AUTH_AUDIENCE

router = APIRouter(prefix="/auth", tags=["auth"])


def _calculate_expiration(payload: dict) -> tuple[int, int]:
    """Helper to convert exp to UNIX timestamp and calculate expires_in."""
    now_ts = int(datetime.utcnow().timestamp())
    exp = (
        int(payload["exp"].timestamp())
        if hasattr(payload["exp"], "timestamp")
        else int(payload["exp"])
    )
    expires_in = max(exp - now_ts, 0)
    return exp, expires_in


@router.post("/login")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)) -> Any:
    """Authenticate user and return JWT tokens with RBAC, tenant info, iat and jti."""
    try:
        response = requests.post(
            f"{USER_SERVICE_URL}/users/verify",
            json={"email": payload.email, "password": payload.password},
            timeout=5,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable",
        ) from exc

    user_data = response.json().get("result", {})
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    user_id = str(user_data.get("id"))
    roles = sorted(user_data.get("roles", []))
    permissions = sorted(user_data.get("permissions", []))
    tenant_id = user_data.get("tenant_id")

    # Create JWT tokens
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


@router.post("/refresh")
async def refresh_token(
    request: Request, payload: RefreshRequest, db: Session = Depends(get_db)
) -> Any:
    """
    Refresh an access token using a valid, non-blacklisted refresh token.
    """
    try:
        token_payload = decode_token(payload.refresh_token)
        jti = token_payload.get("jti", str(uuid.uuid4()))

        # Check if refresh token is blacklisted
        is_bl = await anyio.to_thread.run_sync(token_blacklist_crud.is_blacklisted, db, jti)
        if is_bl:
            raise HTTPException(
                status_code=401,
                detail=f"Refresh token with jti={jti} is blacklisted",
            )

        user_id = token_payload.get("sub")
        roles = token_payload.get("roles", [])
        permissions = token_payload.get("permissions", [])
        tenant_id = token_payload.get("tenant_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

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
            "meta": {
                "api_version": "v1",
                "request_path": str(request.url.path),
            },
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/logout")
async def logout(request: Request, payload: RefreshRequest, db: Session = Depends(get_db)) -> Any:
    """
    Blacklist a refresh token so it cannot be reused.
    Raises exception if token is already blacklisted.
    """
    try:
        token_payload = decode_token(payload.refresh_token)
        jti = token_payload.get("jti", str(uuid.uuid4()))

        # Run DB insert in thread-safe context
        def blacklist_token():
            token_blacklist_crud.add(db, jti)

        try:
            await anyio.to_thread.run_sync(blacklist_token)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Token with jti={jti} is already blacklisted",
            )

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
            "meta": {
                "api_version": "v1",
                "request_path": str(request.url.path),
            },
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
