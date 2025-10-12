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
from sqlalchemy.pool import QueuePool

from app.core.config import get_settings

# -------------------------------------------------------
# Configuration
# -------------------------------------------------------
settings = get_settings()

# -------------------------------------------------------
# Async SQLAlchemy engine
# -------------------------------------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    future=True,
)

# -------------------------------------------------------
# Async session factory
# -------------------------------------------------------
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# -------------------------------------------------------
# Async context manager for DB session
# -------------------------------------------------------
@asynccontextmanager
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
