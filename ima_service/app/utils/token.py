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
    # Cast to str for MyPy (even if jwt.encode returns bytes)
    return cast(str, token)


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT access token.

    Args:
        data (Dict[str, Any]): Payload data (e.g., {"sub": user_id})

    Returns:
        str: JWT access token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return _encode_token(to_encode, "HS256")


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.

    Args:
        data (Dict[str, Any]): Payload data

    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return _encode_token(to_encode, "HS256")


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token.

    Args:
        token (str): JWT string

    Returns:
        Dict[str, Any]: Decoded payload
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
