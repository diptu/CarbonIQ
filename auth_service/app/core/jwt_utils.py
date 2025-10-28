"""Utility functions for creating and decoding JWT tokens."""

from datetime import datetime, timedelta
from typing import Any, Dict, cast

from jose import jwt

from app.core.config import settings


def create_access_token(subject: str) -> str:
    """Generate a JWT access token with expiration time in minutes."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token: Any = jwt.encode(
        {"sub": subject, "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return cast(str, token)


def create_refresh_token(subject: str) -> str:
    """Generate a JWT refresh token with expiration time in days."""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token: Any = jwt.encode(
        {"sub": subject, "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return cast(str, token)


def decode_token(token: str) -> Dict[str, Any]:
    """Decode a JWT token and return its payload."""
    payload: Any = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return cast(Dict[str, Any], payload)
