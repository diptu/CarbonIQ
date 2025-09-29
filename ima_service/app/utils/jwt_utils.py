# app/utils/jwt_utils.py
"""JWT token creation and decoding utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, cast

import jwt
from pydantic import SecretStr

from ..core.config import get_settings

settings = get_settings()


def _get_secret_key() -> str:
    """Return the JWT secret key as plain string, unwrapping SecretStr if needed."""
    key = settings.SECRET_KEY
    if isinstance(key, SecretStr):
        return key.get_secret_value()
    return str(key)


def _encode_token(data: Dict[str, Any], algorithm: str) -> str:
    """
    Encode a JWT payload and return a string token.

    Args:
        data (Dict[str, Any]): Payload to encode.
        algorithm (str): JWT signing algorithm.

    Returns:
        str: JWT token as string.
    """
    return cast(str, jwt.encode(data, _get_secret_key(), algorithm=algorithm))


def create_access_token(
    data: Dict[str, Any], expires_minutes: int | None = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data (Dict[str, Any]): Payload data (e.g., {"sub": user_id})
        expires_minutes (int | None): Expiry in minutes
        (defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        str: JWT access token
    """
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = data.copy()
    payload.update({"exp": expire, "type": "access"})
    return cast(str, _encode_token(payload, settings.JWT_ALGORITHM))


def create_refresh_token(data: Dict[str, Any], expires_days: int | None = None) -> str:
    """
    Create a JWT refresh token.

    Args:
        data (Dict[str, Any]): Payload data (e.g., {"sub": user_id})
        expires_days (int | None): Expiry in days
        (defaults to settings.REFRESH_TOKEN_EXPIRE_DAYS)

    Returns:
        str: JWT refresh token
    """
    expire = datetime.now(timezone.utc) + timedelta(
        days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = data.copy()
    payload.update({"exp": expire, "type": "refresh"})
    return _encode_token(payload, settings.JWT_ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.

    Args:
        token (str): JWT string

    Returns:
        Dict[str, Any]: Decoded payload
    """
    return jwt.decode(token, _get_secret_key(), algorithms=[settings.JWT_ALGORITHM])
