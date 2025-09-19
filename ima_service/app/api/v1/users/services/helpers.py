# FILE: ima_service/app/api/v1/users/services/helpers.py
"""Password hashing helpers (passlib)."""

from __future__ import annotations

from typing import Any, cast

# passlib has no type stubs; with mypy `ignore_missing_imports = true`,
# this import is `Any`.
from passlib.context import CryptContext

_pwd_ctx: Any = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Return a bcrypt hash for the given plaintext password."""
    return cast(str, _pwd_ctx.hash(plain))


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plaintext matches the given bcrypt hash."""
    return bool(_pwd_ctx.verify(plain, hashed))
