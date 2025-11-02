"""Authentication routes for login, token refresh, and logout."""

import uuid
from datetime import datetime
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.jwt_utils import create_access_token, create_refresh_token, decode_token
from app.crud.token_blacklist import token_blacklist_crud
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshRequest

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
    """
    Authenticate a user via User Service and return JWT with RBAC info
    and token expiry included in the response.
    """
    # Call User Service to verify credentials
    try:
        response = requests.post(
            f"{USER_SERVICE_URL}/users/verify",
            json={"email": payload.email, "password": payload.password},
            timeout=5,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User service unavailable",
        ) from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user_data = response.json().get("data", {})
    user_id = str(user_data.get("id"))
    roles = sorted(user_data.get("roles", []))
    permissions = sorted(user_data.get("permissions", []))
    tenant_id = user_data.get("tenant_id")

    # Create JWT tokens and payloads
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
            "access_token": access_token,
            "refresh_token": refresh_token,
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


@router.post("/refresh")
def refresh_token(request: Request, payload: RefreshRequest, db: Session = Depends(get_db)) -> Any:
    """
    Issue new tokens using a valid refresh token and return structured response.
    """
    try:
        token_payload = decode_token(payload.refresh_token)
        jti = token_payload.get("jti", str(uuid.uuid4()))

        if token_blacklist_crud.is_blacklisted(db, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token blacklisted"
            )

        user_id = token_payload.get("sub")
        roles = token_payload.get("roles", [])
        permissions = token_payload.get("permissions", [])
        tenant_id = token_payload.get("tenant_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Generate new tokens
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

    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


@router.post("/logout")
def logout(request: Request, payload: RefreshRequest, db: Session = Depends(get_db)) -> Any:
    """
    Blacklist a refresh token so it cannot be reused.
    """
    try:
        token_payload = decode_token(payload.refresh_token)
        jti = token_payload.get("jti", str(uuid.uuid4()))
        token_blacklist_crud.add(db, jti)

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
