# app/core/security.py
"""
Security utilities for password hashing and JWT token management.

Provides:
- Password hashing & verification using bcrypt (Passlib)
- JWT access & refresh token creation
- Token verification with multi-tenant RBAC context
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Union
from uuid import UUID

from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from .config import get_settings

settings = get_settings()
logger = logging.getLogger("carboniq.security")

# -------------------------------
# Password Hashing
# -------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------------
# JWT Token Utilities
# -------------------------------
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS: int = settings.REFRESH_TOKEN_EXPIRE_DAYS


def _utcnow() -> datetime:
    """Return current UTC time."""
    return datetime.now(timezone.utc)


def create_access_token(
    user_id: Union[UUID, str],
    tenant_id: Union[UUID, str],
    roles: List[str],
    expires_minutes: Optional[int] = None,
) -> str:
    """Create a JWT access token with user_id, tenant_id, roles, and expiry."""
    now = _utcnow()
    expire = now + timedelta(minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Union[str, List[str], datetime]] = {
        "sub": str(user_id),
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "type": "access",
        "iat": now,
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_refresh_token(
    user_id: Union[UUID, str],
    tenant_id: Union[UUID, str],
    expires_days: Optional[int] = None,
) -> str:
    """Create a JWT refresh token with user_id and tenant_id."""
    now = _utcnow()
    expire = now + timedelta(days=expires_days or REFRESH_TOKEN_EXPIRE_DAYS)
    payload: Dict[str, Union[str, datetime]] = {
        "sub": str(user_id),
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "type": "refresh",
        "iat": now,
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    Returns the payload if valid, otherwise None.
    Handles invalid, expired, and malformed tokens gracefully.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        return payload

    except ExpiredSignatureError:
        logger.warning("JWT token expired.")
        return None
    except JWTError as e:
        logger.warning("JWT verification failed: %s", e)
        return None
