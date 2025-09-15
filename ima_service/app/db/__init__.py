#app/db/__init__.py
"""Database package exports.

This package centralizes database primitives for the application.

Exports
-------
Base
    Declarative base for SQLAlchemy models.
AsyncSession
    SQLAlchemy async session type (re-export for convenience).
AsyncSessionManager
    OOP manager wrapping engine + session factory with caching.
get_session_manager
    Lazily construct and cache an `AsyncSessionManager`.
get_db
    FastAPI dependency that yields an `AsyncSession`.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base
from .session import AsyncSessionManager, get_db, get_session_manager

__all__ = [
    "Base",
    "AsyncSession",
    "AsyncSessionManager",
    "get_session_manager",
    "get_db",
]
