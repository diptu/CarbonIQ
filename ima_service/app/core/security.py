# app/core/security.py
"""Security utilities for authentication, password hashing, and JWT.

Pandas-style docstring
----------------------
Provides:

- Secure password hashing and verification (bcrypt)
- JWT creation and validation with Pydantic settings
- Role-based access control helpers
- Optional logging for audit and security events
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional

import bcrypt
import jwt
from jwt import PyJWTError

from app.core.config import get_settings
from app.core.exceptions import raise_invalid_token
from app.core.logger import audit_logger

settings = get_settings()


# --- Password hashing & verification --------------------------------
def hash_password(plain_password: str) -> str:
    """Hash plain password using bcrypt.

    Args
    ----
    plain_password : str
        Raw password to hash.

    Returns
    -------
    str
        Hashed password.
    """
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password.

    Args
    ----
    plain_password : str
        Raw password.
    hashed_password : str
        Hashed password stored in DB.

    Returns
    -------
    bool
        True if password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


# --- JWT creation & verification ------------------------------------
def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    tenant_id: Optional[str] = None,
) -> str:
    """Create a JWT access token.

    Args
    ----
    subject : str
        User identifier (e.g., email or user_id)
    expires_delta : Optional[timedelta]
        Expiration time override
    tenant_id : Optional[str]
        Optional tenant ID to include in claims

    Returns
    -------
    str
        Encoded JWT token
    """
    expire = datetime.utcnow() + (expires_delta or settings.access_token_expires)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }
    if tenant_id:
        payload["tenant_id"] = tenant_id
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    audit_logger.info(
        f"Access token created for user {subject}", extra={"tenant_id": tenant_id}
    )
    return token


def decode_token(token: str, verify_exp: bool = True) -> dict[str, Any]:
    """Decode and validate JWT token.

    Args
    ----
    token : str
        JWT token to decode
    verify_exp : bool
        Whether to enforce expiration

    Returns
    -------
    dict[str, Any]
        Decoded token payload

    Raises
    ------
    HTTPException
        If token is invalid or expired
    """
    try:
        options = {"verify_exp": verify_exp}
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
            options=options,
        )
        return payload
    except PyJWTError:
        audit_logger.warning("Invalid or expired token", extra={"token": token})
        raise_invalid_token()


# --- RBAC Helpers ---------------------------------------------------
def has_permission(user_permissions: list[str], required_permission: str) -> bool:
    """Check if user has required permission.

    Args
    ----
    user_permissions : list[str]
        List of permission names assigned to user
    required_permission : str
        Permission to check

    Returns
    -------
    bool
        True if user has permission
    """
    return required_permission in user_permissions


def has_role(user_roles: list[str], required_role: str) -> bool:
    """Check if user has a specific role.

    Args
    ----
    user_roles : list[str]
        List of roles assigned to user
    required_role : str
        Role to check

    Returns
    -------
    bool
        True if role is assigned
    """
    return required_role in user_roles


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    tenant_id: Optional[str] = None,
) -> str:
    """Create a JWT refresh token.

    Args
    ----
    subject : str
        User identifier (e.g., email or user_id)
    expires_delta : Optional[timedelta]
        Expiration time override (default: settings.refresh_token_expires)
    tenant_id : Optional[str]
        Optional tenant ID to include in claims

    Returns
    -------
    str
        Encoded JWT refresh token
    """
    expire = datetime.utcnow() + (expires_delta or settings.refresh_token_expires)
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "type": "refresh",
    }
    if tenant_id:
        payload["tenant_id"] = tenant_id

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    audit_logger.info(
        f"Refresh token created for user {subject}", extra={"tenant_id": tenant_id}
    )
    return token
