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
    return_payload: bool = False,
) -> Any:
    """
    Generate a JWT access token with RBAC, tenant, issuer, and audience claims.

    Args:
        return_payload (bool): If True, returns (token, payload) instead of just token.
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {
        "sub": sub,
        "iss": iss,
        "aud": aud,
        "exp": expire,
        "jti": str(uuid.uuid4()),
        "roles": roles or [],
        "permissions": permissions or [],
        "tenant_id": tenant_id,
    }

    token: str = cast(str, jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM))
    return (token, payload) if return_payload else token


def create_refresh_token(
    sub: str,
    return_payload: bool = False,
) -> Any:
    """
    Generate a JWT refresh token with expiration time in days and unique JTI.

    Args:
        return_payload (bool): If True, returns (token, payload) instead of just token.
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: Dict[str, Any] = {
        "sub": sub,
        "exp": expire,
        "jti": str(uuid.uuid4()),
    }

    token: str = cast(str, jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM))
    return (token, payload) if return_payload else token


def decode_token(
    token: str,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Decode a JWT token and return its payload.

    Args:
        secret_key (Optional[str]): Secret key for decoding. Defaults to settings.SECRET_KEY.
        algorithm (Optional[str]): Algorithm for decoding. Defaults to settings.ALGORITHM.

    Raises:
        JWTError: If the token is invalid or expired.
    """
    secret_key = secret_key or settings.SECRET_KEY
    algorithm = algorithm or settings.ALGORITHM

    try:
        payload: Any = jwt.decode(token, secret_key, algorithms=[algorithm])
        return cast(Dict[str, Any], payload)
    except JWTError as exc:
        raise JWTError(f"Invalid or expired token: {exc}") from exc
