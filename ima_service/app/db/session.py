# FILE: ima_service/app/db/session.py
"""
Async SQLAlchemy session utilities.

- Neon-friendly TLS defaults (SSL on for *.neon.tech).
- Local Postgres convenience (no SSL for localhost/127.0.0.1/::1 unless forced).
- Lazy, cached engine + session factory (safe at import time).
- Dependency helpers for FastAPI (`get_db`) with clean HTTP errors.
"""

from __future__ import annotations

import ipaddress
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import Any, Final, cast
from urllib.parse import urlparse

from fastapi import HTTPException, status
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ima_service.app.core.config import Settings, get_settings

LOG: Final = logging.getLogger(__name__)


def _is_local_host(host: str) -> bool:
    """Return True if host points to local loopback."""
    if not host:
        return False
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_loopback
    except ValueError:
        return host in {"localhost", "ip6-localhost"}


def _ssl_connect_args(
    ssl_mode: str | None, uri: str | None
) -> dict[str, object]:
    """
    Translate env to asyncpg 'ssl' arg.

    Rules
    -----
    - If host ends with '.neon.tech' => {'ssl': True} (force TLS).
    - If ssl_mode in {disable, off, false, 0, ""} => {}.
    - If host is local and ssl_mode not explicitly 'require' => {}.
    - Otherwise => {'ssl': True}.
    """
    host = ""
    if uri:
        # urlparse() is safe; it doesn't raise for arbitrary strings.
        host = (urlparse(uri).hostname or "").strip().lower()
        if host.endswith("neon.tech"):
            return {"ssl": True}

    mode = (ssl_mode or "").strip().lower()
    if mode in {"", "disable", "off", "false", "0"}:
        return {}
    if _is_local_host(host) and mode not in {"require", "on", "true", "1"}:
        return {}
    return {"ssl": True}


@dataclass
class AsyncSessionManager:
    """
    Manages SQLAlchemy async engine and session factory.

    Parameters
    ----------
    uri:
        SQLAlchemy async DSN (e.g., postgresql+asyncpg://user:pass@host/db).
    debug:
        If True, SQLAlchemy echo and startup diagnostics are enabled.
    ssl_mode:
        String directive for TLS ("require"/"disable"/etc.).
        See _ssl_connect_args for details.
    """

    uri: str
    debug: bool = False
    ssl_mode: str | None = "require"

    @cached_property
    def engine(self) -> AsyncEngine:
        """Create and cache the async engine."""
        args = _ssl_connect_args(self.ssl_mode, self.uri)
        if self.debug:
            host = urlparse(self.uri).hostname or "?"
            LOG.info(
                "DB engine init host=%s ssl=%s", host, bool(args.get("ssl"))
            )
        return create_async_engine(
            self.uri,
            echo=self.debug,
            connect_args=args,
            pool_pre_ping=True,
        )

    @cached_property
    def factory(self) -> async_sessionmaker[AsyncSession]:
        """Create and cache the session factory."""
        return async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def dispose(self) -> None:
        """Dispose the engine (useful for tests/shutdown)."""
        await self.engine.dispose()

    async def __call__(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield a session (internal helper for `get_db`)."""
        async with self.factory() as session:
            yield session

    @classmethod
    def from_settings(
        cls, settings: Settings | None = None
    ) -> "AsyncSessionManager":
        """Build from Pydantic settings with friendly error messages."""
        try:
            cfg = settings or get_settings()
        except PydanticValidationError as exc:
            raise RuntimeError(f"Invalid database settings: {exc}") from exc

        # ✅ use effective_uri so DB_URI (or parts) override defaults
        uri = getattr(cfg.database, "effective_uri", cfg.database.uri)

        return cls(
            uri=uri,
            debug=cfg.debug,
            ssl_mode=cfg.database.ssl_mode,
        )


@lru_cache(maxsize=1)
def get_session_manager() -> AsyncSessionManager:
    """
    Return a cached `AsyncSessionManager`.

    Notes
    -----
    - Uses lru_cache to avoid multiple engine creations.
    - Call `refresh_session_manager()` if env changes at runtime.
    """
    return AsyncSessionManager.from_settings()


def refresh_session_manager() -> None:
    """Clear cache so subsequent calls re-read configuration."""
    try:
        # mypy knows about cache_clear if we cast to Any; avoids unused-ignore.
        cast(Any, get_session_manager).cache_clear()
    except AttributeError:  # pragma: no cover
        # If the cache was already cleared or the attribute is missing.
        pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency: yield an `AsyncSession`.

    Raises
    ------
    HTTPException(500)
        If manager creation or connection fails.
    """
    try:
        manager = get_session_manager()
    except RuntimeError as exc:
        # Config/validation errors bubble as RuntimeError from `from_settings()`
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database configuration error: {exc}",
        ) from exc

    try:
        async for session in manager():
            yield session
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {exc}",
        ) from exc
