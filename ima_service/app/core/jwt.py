# app/core/jwt.py
"""Simplified JWT token creation and decoding utilities with tenant and role claims."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, cast, Optional, List

import jwt
from pydantic import SecretStr

from app.core.config import get_settings

settings = get_settings()


def _get_secret_key() -> str:
    """Return the JWT secret key as plain string."""
    key = settings.SECRET_KEY
    if isinstance(key, SecretStr):
        return key.get_secret_value()
    return str(key)


def _encode_token(data: Dict[str, Any], algorithm: str) -> str:
    """Encode a JWT payload into a token string."""
    return cast(str, jwt.encode(data, _get_secret_key(), algorithm=algorithm))


def create_access_token(
    user_id: str,
    tenant_id: Optional[str] = None,
    roles: Optional[List[str]] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    """Create a JWT access token including tenant_id and roles."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload: Dict[str, Any] = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "roles": roles or [],
        "exp": expire,
        "iat": now,
        "type": "access",
    }

    return _encode_token(payload, settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: str,
    tenant_id: Optional[str] = None,
    roles: Optional[List[str]] = None,
    expires_days: Optional[int] = None,
) -> str:
    """Create a JWT refresh token including tenant_id and roles."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload: Dict[str, Any] = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "roles": roles or [],
        "exp": expire,
        "iat": now,
        "type": "refresh",
    }

    return _encode_token(payload, settings.JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token and return payload."""
    try:
        payload = jwt.decode(
            token,
            _get_secret_key(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        return cast(Dict[str, Any], payload)
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidTokenError as exc:
        raise Exception(f"Invalid token: {exc}")
