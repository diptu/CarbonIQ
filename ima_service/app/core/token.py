# app/core/token.py
"""JWT token creation and decoding utilities."""

from datetime import datetime, timedelta
from typing import Any, Dict, cast

import jwt

from ..core.config import get_settings

settings = get_settings()


def _encode_token(data: Dict[str, Any], algorithm: str) -> str:
    """
    Encode a JWT payload and return a string token.

    Args:
        data (Dict[str, Any]): Payload to encode.
        algorithm (str): JWT signing algorithm.

    Returns:
        str: JWT token as string.
    """
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=algorithm)
    return cast(str, token)


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT access token.

    Args:
        data (Dict[str, Any]): Payload data (e.g., {"user_id": user.id})

    Returns:
        str: JWT access token
    """
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire, "type": "access"})
    return _encode_token(payload, "HS256")


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.

    Args:
        data (Dict[str, Any]): Payload data

    Returns:
        str: JWT refresh token
    """
    payload = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire, "type": "refresh"})
    return _encode_token(payload, "HS256")


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.

    Args:
        token (str): JWT string

    Returns:
        Dict[str, Any]: Decoded payload

    Raises:
        jwt.ExpiredSignatureError: If the token has expired.
        jwt.InvalidTokenError: If the token is invalid.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
