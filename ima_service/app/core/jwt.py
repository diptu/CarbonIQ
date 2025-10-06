# app/core/jwt.py
"""Simplified JWT token creation and decoding utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, cast

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
    data: Dict[str, Any], expires_minutes: int | None = None
) -> str:
    """Create a JWT access token with minimal claims."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = data.copy()
    payload.update(
        {
            "exp": expire,
            "iat": now,
            "type": "access",
        }
    )

    return _encode_token(payload, settings.JWT_ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_days: int | None = None) -> str:
    """Create a JWT refresh token with minimal claims."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS)

    payload = data.copy()
    payload.update(
        {
            "exp": expire,
            "iat": now,
            "type": "refresh",
        }
    )

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
