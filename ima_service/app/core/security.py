"""
app.core.security
Security utilities for password hashing and JWT token management.
Handles:
  - Password hashing and verification
  - Access/refresh JWT creation
  - Token decoding and verification (RBAC + multi-tenant)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, List, Union
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
    """Return current UTC time (naive)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def create_access_token(
    user_id: Union[UUID, str],
    tenant_id: Union[UUID, str],
    roles: List[str],
    expires_minutes: Optional[int] = None,
) -> str:
    """
    Create JWT access token with user_id, tenant_id, roles, and expiry.
    """
    expire = _utcnow() + timedelta(
        minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": str(user_id),
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "type": "access",
        "exp": expire,
        "iat": _utcnow(),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_refresh_token(user_id: Union[UUID, str], tenant_id: Union[UUID, str]) -> str:
    """
    Create JWT refresh token for a user.
    """
    expire = _utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "type": "refresh",
        "exp": expire,
        "iat": _utcnow(),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


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
