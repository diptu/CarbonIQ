# FILE: ima_service/app/api/v1/users/__init__.py
"""Users API package exports (router + services)."""

from __future__ import annotations

# Public router
from .router import router  # noqa: F401

# Re-export service interfaces / factories via the services package
from .services import (  # noqa: F401
    DatabaseUserService,
    RedisTokenStore,  # alias to AsyncRedisTokenStore
    UserService,
    get_user_service,
)

__all__ = [
    "router",
    "UserService",
    "DatabaseUserService",
    "get_user_service",
    "RedisTokenStore",
]
