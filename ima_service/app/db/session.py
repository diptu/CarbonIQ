# app/db/session.py
"""
Async SQLAlchemy session setup for IMA Service (Neon/Postgres).

Features
--------
- Async engine with connection pooling
- AsyncSession factory
- Async context manager for DB access (get_db)
- FastAPI dependency-compatible
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import get_settings  # type:ignore[import-not-found]

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------
settings = get_settings()

# -------------------------------------------------------
# Async SQLAlchemy engine
# -------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,  # must use postgresql+asyncpg://...
    echo=settings.DEBUG,
    pool_size=20,  # max number of persistent connections
    max_overflow=10,  # additional temporary connections allowed beyond pool_size
    pool_timeout=30,  # seconds to wait for connection from pool
    pool_recycle=1800,  # recycle connection after 30 minutes
    # asyncpg driver handles pooling internally
    connect_args={"ssl": True},  # enable SSL for asyncpg
)

# -------------------------------------------------------
# Async session factory
# -------------------------------------------------------
async_session_factory = sessionmaker(  # type: ignore[call-overload]
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncIterator[AsyncSession]:
    """
    Provide a transactional scope around a series of database operations.

    Yields
    ------
    AsyncSession
        An async SQLAlchemy session instance.

    Example
    -------
    async with get_db() as session:
        result = await session.execute(select(User))
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
