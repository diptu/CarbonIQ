from __future__ import annotations

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from functools import cached_property, lru_cache

from fastapi import HTTPException, status
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ima_service.app.core.config import Settings, get_settings


def _ssl_connect_args(ssl_mode: str | None) -> dict[str, object]:
    """Translate DB_SSL_MODE to asyncpg 'ssl' arg."""
    if ssl_mode is None:
        return {"ssl": True}
    mode = ssl_mode.strip().lower()
    if mode in {"", "disable", "off", "false", "0"}:
        return {}
    return {"ssl": True}


@dataclass
class AsyncSessionManager:
    """Create and manage SQLAlchemy AsyncSession."""

    uri: str
    debug: bool = False
    ssl_mode: str | None = "require"

    @cached_property
    def engine(self) -> AsyncEngine:
        return create_async_engine(
            self.uri,
            echo=self.debug,
            connect_args=_ssl_connect_args(self.ssl_mode),
            pool_pre_ping=True,
        )

    @cached_property
    def factory(self) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def dispose(self) -> None:
        await self.engine.dispose()

    async def __call__(self) -> AsyncGenerator[AsyncSession, None]:
        try:
            async with self.factory() as session:
                yield session
        except Exception as exc:  # pylint: disable=broad-except
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database connection error: {exc}",
            ) from exc

    @classmethod
    def from_settings(
        cls, settings: Settings | None = None
    ) -> "AsyncSessionManager":
        try:
            cfg = settings or get_settings()
        except PydanticValidationError as exc:
            raise RuntimeError(f"Invalid database settings: {exc}") from exc
        return cls(uri=cfg.database.uri, debug=cfg.debug,
                   ssl_mode=cfg.database.ssl_mode)


@lru_cache(maxsize=1)
def get_session_manager() -> AsyncSessionManager:
    return AsyncSessionManager.from_settings()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        manager = get_session_manager()
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database configuration error: {exc}",
        ) from exc

    try:
        async for session in manager():
            yield session
    except HTTPException:
        raise
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection error: {exc}",
        ) from exc
