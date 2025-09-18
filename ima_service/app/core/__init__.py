# FILE: ima_service/app/core/__init__.py
"""
Core package façade.

Re-exports stable, high-level helpers while keeping import-time side effects
to a minimum.
"""

from __future__ import annotations

from .config import get_settings  # lightweight
from .logging import setup_logging  # call in startup
from .redis_cache import (
    RedisClientError,
    close_redis_client,
    get_redis_client,
)

__all__ = [
    "get_settings",
    "setup_logging",
    "get_redis_client",
    "close_redis_client",
    "RedisClientError",
]
