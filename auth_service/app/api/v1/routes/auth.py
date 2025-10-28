"""Authentication routes for login, token refresh, and logout."""

import uuid
from typing import Any, Dict

import requests
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.jwt_utils import create_access_token, create_refresh_token, decode_token
from app.crud.token_blacklist import token_blacklist_crud
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshRequest, Token

USER_SERVICE_URL = "http://user-service:8001"

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:  # pylint: disable=unused-argument
    """
    Authenticate a user by calling the User Service.
    Returns access and refresh tokens if credentials are valid.
    """
    try:
        response = requests.post(
            f"{USER_SERVICE_URL}/users/verify",
            json={"email": request.email, "password": request.password},
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

    user_data = response.json()
    user_id = str(user_data.get("id"))

    access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Issue new tokens using a valid refresh token.
    """
    try:
        payload = decode_token(request.refresh_token)
        jti = payload.get("jti", str(uuid.uuid4()))

        if token_blacklist_crud.is_blacklisted(db, jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token blacklisted"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        access_token = create_access_token(user_id)
        new_refresh_token = create_refresh_token(user_id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


@router.post("/logout")
def logout(request: RefreshRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Blacklist a refresh token so it cannot be reused.
    """
    try:
        payload = decode_token(request.refresh_token)
        jti = payload.get("jti", str(uuid.uuid4()))

        token_blacklist_crud.add(db, jti)
        return {"detail": "Successfully logged out"}

    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
