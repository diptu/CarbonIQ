"""Utility functions for creating and decoding JWT tokens with RBAC and tenant claims."""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(
    sub: str,
    iss: str = "auth.carboniq.com",
    aud: str = "api.carboniq.com",
    roles: Optional[List[str]] = None,
    permissions: Optional[List[str]] = None,
    tenant_id: Optional[str] = None,
) -> str:
    """Generate a JWT access token with RBAC, tenant, issuer, and audience claims."""
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {
        "sub": sub,
        "iss": iss,
        "aud": aud,
        "exp": expire,
        "jti": str(uuid.uuid4()),  # unique token ID
        "roles": roles or [],
        "permissions": permissions or [],
        "tenant_id": tenant_id,
    }

    token: Any = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return cast(str, token)


def create_refresh_token(sub: str) -> str:
    """Generate a JWT refresh token with expiration time in days and unique JTI."""
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: Dict[str, Any] = {
        "sub": sub,
        "exp": expire,
        "jti": str(uuid.uuid4()),  # unique token ID for blacklist tracking
    }
    token: Any = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return cast(str, token)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token and return its payload.

    Raises JWTError if the token is invalid or expired.
    """
    try:
        payload: Any = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return cast(Dict[str, Any], payload)
    except JWTError as exc:
        raise JWTError(f"Invalid or expired token: {exc}") from exc
