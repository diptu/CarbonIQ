# app/core/security.py
"""
Production-ready security utilities for IMA Service.

Includes:
- Password hashing and verification (bcrypt)
- JWT access & refresh token creation
- JWT decoding and validation with tenant and role claims
- Standardized exception handling
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from .exceptions import BadRequestException, UnauthorizedException
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from pydantic import SecretStr

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger("carboniq:security")

# -------------------------------
# Password hashing
# -------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return bcrypt hash for a plaintext password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------------
# JWT Utilities
# -------------------------------
def _get_secret_key() -> str:
    """Return SECRET_KEY as plain string (supports SecretStr)."""
    key = settings.SECRET_KEY
    if isinstance(key, SecretStr):
        return key.get_secret_value()
    return str(key)


def _utcnow() -> datetime:
    """Return current UTC datetime with tzinfo."""
    return datetime.now(timezone.utc)


def _build_payload(
    user_id: Union[UUID, str],
    tenant_id: Optional[Union[UUID, str]],
    roles: Optional[List[str]],
    token_type: str,
    expires_at: datetime,
) -> Dict[str, Union[str, List[str], datetime]]:
    """Construct standard JWT payload with claims."""
    return {
        "sub": str(user_id),
        "user_id": str(user_id),
        "tenant_id": str(tenant_id) if tenant_id else None,
        "roles": roles or [],
        "type": token_type,
        "iat": _utcnow(),
        "exp": expires_at,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "jti": str(uuid4()),
    }


def create_access_token(
    user_id: Union[UUID, str],
    tenant_id: Optional[Union[UUID, str]] = None,
    roles: Optional[List[str]] = None,
    expires_minutes: Optional[int] = None,
) -> str:
    """Create a signed JWT access token with tenant and role claims."""
    now = _utcnow()
    exp = now + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = _build_payload(user_id, tenant_id, roles, "access", exp)
    return jwt.encode(payload, _get_secret_key(), algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: Union[UUID, str],
    tenant_id: Optional[Union[UUID, str]] = None,
    expires_days: Optional[int] = None,
) -> str:
    """Create a signed JWT refresh token."""
    now = _utcnow()
    exp = now + timedelta(days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = _build_payload(
        user_id, tenant_id, roles=None, token_type="refresh", expires_at=exp
    )
    return jwt.encode(payload, _get_secret_key(), algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    """Decode and validate a JWT token.

    Verifies issuer, audience, expiry, and optional token type.

    Raises
    ------
    UnauthorizedException: Token expired or invalid.
    BadRequestException: Malformed token or type mismatch.
    """
    try:
        options = {"require": ["exp", "iat", "sub", "jti"]}
        payload = jwt.decode(
            token,
            _get_secret_key(),
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options=options,
            leeway=10,  # allow small clock skew
        )
    except ExpiredSignatureError as exc:
        raise UnauthorizedException(detail="Token has expired") from exc
    except JWTError as exc:
        raise UnauthorizedException(detail="Invalid authentication token") from exc
    except Exception as exc:  # pragma: no cover
        raise BadRequestException(detail="Failed to decode token") from exc

    if expected_type and payload.get("type") != expected_type:
        raise BadRequestException(
            detail=f"Token type mismatch: expected '{expected_type}', got '{payload.get('type')}'"
        )

    if "sub" not in payload:
        raise BadRequestException(detail="Token missing subject (sub) claim")

    return payload.copy()


def verify_token(token: str, expected_type: Optional[str] = None) -> Dict[str, Any]:
    """Wrapper around decode_token that returns payload with ISO datetime strings."""
    payload = decode_token(token, expected_type=expected_type)
    for key in ("exp", "iat"):
        if key in payload and isinstance(payload[key], datetime):
            payload[key] = payload[key].isoformat()
    return payload.copy()
