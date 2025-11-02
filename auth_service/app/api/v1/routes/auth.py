"""Authentication routes for login, token refresh, and logout."""

import uuid
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.jwt_utils import create_access_token, create_refresh_token, decode_token
from app.core.response import build_response_from_request
from app.crud.token_blacklist import token_blacklist_crud
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshRequest

USER_SERVICE_URL = settings.USER_SERVICE_URL
AUTH_ISSUER = settings.AUTH_ISSUER
AUTH_AUDIENCE = settings.AUTH_AUDIENCE

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
@router.post("/login")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)) -> Any:
    """
    Authenticate a user by calling the User Service.
    Returns rich JWT with sub, iss, aud, roles, permissions, tenant_id, etc.
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

    # User service returns full RBAC info now
    user_response = response.json().get("data", {})

    user_id = str(user_response.get("id"))
    roles = user_response.get("roles", [])
    permissions = user_response.get("permissions", [])
    tenant_id = user_response.get("tenant_id")

    # Create JWT tokens with RBAC claims
    access_token = create_access_token(
        sub=user_id,
        iss=AUTH_ISSUER,
        aud=AUTH_AUDIENCE,
        roles=roles,
        permissions=permissions,
        tenant_id=tenant_id,
    )
    refresh_token = create_refresh_token(sub=user_id)

    # Return standardized API response with trace/correlation info
    return build_response_from_request(
        request,
        data={
            "sub": user_id,
            "iss": AUTH_ISSUER,
            "aud": AUTH_AUDIENCE,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "roles": roles,
            "permissions": permissions,
            "tenant_id": tenant_id,
        },
    )


@router.post("/refresh")
def refresh_token(request: Request, payload: RefreshRequest, db: Session = Depends(get_db)) -> Any:
    """
    Issue new tokens using a valid refresh token.
    """
    try:
        token_payload = decode_token(payload.refresh_token)
        jti = token_payload.get("jti", str(uuid.uuid4()))

        if token_blacklist_crud.is_blacklisted(db, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token blacklisted",
            )

        user_id = token_payload.get("sub")
        roles = token_payload.get("roles", [])
        permissions = token_payload.get("permissions", [])
        tenant_id = token_payload.get("tenant_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        access_token = create_access_token(
            sub=user_id,
            iss=AUTH_ISSUER,
            aud=AUTH_AUDIENCE,
            roles=roles,
            permissions=permissions,
            tenant_id=tenant_id,
        )
        new_refresh_token = create_refresh_token(sub=user_id)

        return build_response_from_request(
            request,
            data={
                "sub": user_id,
                "iss": AUTH_ISSUER,
                "aud": AUTH_AUDIENCE,
                "access_token": access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
                "roles": roles,
                "permissions": permissions,
                "tenant_id": tenant_id,
            },
        )

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

        return build_response_from_request(
            request,
            data={"detail": "Successfully logged out"},
        )

    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
