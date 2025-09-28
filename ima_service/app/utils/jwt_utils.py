# app/utils/jwt_utils.py
"""JWT token creation and decoding utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import jwt
from pydantic import SecretStr
from app.core.config import get_settings

settings = get_settings()


def _get_secret_key() -> str:
    """Return the JWT secret key as plain string."""
    key = settings.SECRET_KEY
    if isinstance(key, SecretStr):
        return key.get_secret_value()  # unwrap SecretStr
    return str(key)


def create_access_token(
    data: Dict[str, Any], expires_minutes: int | None = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data (Dict[str, Any]): Payload data (e.g., {"sub": user_id})
        expires_minutes (int | None): Expiry in minutes (defaults to env setting)

    Returns:
        str: JWT access token
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "access"})
    token = jwt.encode(to_encode, _get_secret_key(), algorithm=settings.JWT_ALGORITHM)
    return token


def create_refresh_token(data: Dict[str, Any], expires_days: int | None = None) -> str:
    """
    Create a JWT refresh token.

    Args:
        data (Dict[str, Any]): Payload data (e.g., {"sub": user_id})
        expires_days (int | None): Expiry in days (defaults to env setting)

    Returns:
        str: JWT refresh token
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode = data.copy()
    to_encode.update({"exp": expire, "type": "refresh"})
    token = jwt.encode(to_encode, _get_secret_key(), algorithm=settings.JWT_ALGORITHM)
    return token


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.

    Args:
        token (str): JWT string

    Returns:
        Dict[str, Any]: Decoded payload
    """
    return jwt.decode(token, _get_secret_key(), algorithms=[settings.JWT_ALGORITHM])
