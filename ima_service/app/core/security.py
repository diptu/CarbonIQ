# app/core/security.py
"""
Security utilities for password hashing and JWT token management.
Handles:
  - Password hashing and verification
  - Access/refresh JWT creation
  - Token decoding and verification (RBAC + multi-tenant)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Union, Dict
from uuid import UUID
import logging

from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# -------------------------------
# Password Hashing
# -------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------------
# JWT Token Utilities
# -------------------------------
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


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
        logger.warning(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during JWT verification: {e}")
        return None


# app/core/security.py
"""Password hashing and verification utilities using bcrypt."""

from passlib.context import CryptContext

# CryptContext for bcrypt hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.

    Args:
        password (str): Plain text password.

    Returns:
        str: Hashed password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain password matches a given hashed password.

    Args:
        plain_password (str): Plain text password to verify.
        hashed_password (str): Existing hashed password.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
