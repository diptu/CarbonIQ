# app/core/security.py
"""
Security utilities for password hashing and JWT token management.

Provides:
- Password hashing & verification using bcrypt (Passlib)
- JWT access & refresh token creation returning AuthToken objects
- Token verification with multi-tenant RBAC context
"""

import logging

from passlib.context import CryptContext

from .config import get_settings

settings = get_settings()
logger = logging.getLogger("carboniq")

# -------------------------------
# Password Hashing
# -------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password safely with bcrypt."""
    return pwd_context.hash(password.encode("utf-8"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password safely."""
    return pwd_context.verify(plain_password.encode("utf-8"), hashed_password)
