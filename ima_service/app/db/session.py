# app/db/session.py
"""Async SQLAlchemy engine and async session factory."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker

from ..core.config import get_settings

settings = get_settings()

# Async engine. DATABASE_URL must use asyncpg driver.
# Example: postgresql+asyncpg://user:pass@host:5432/dbname
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=bool(settings.DEBUG),
    future=True,
    pool_pre_ping=True,
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    future=True,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession.

    Usage:
        async def endpoint(db: AsyncSession = Depends(get_db)):
            await db.execute(...)
    """
    async with AsyncSessionLocal() as session:
        yield session
