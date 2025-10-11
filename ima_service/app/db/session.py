# app/db/session.py
# type: ignore
"""
Async SQLAlchemy session setup for IMA Service (Neon/Postgres).

Features
--------
- Async engine with connection pooling
- AsyncSession factory
- FastAPI dependency injection
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from app.core.config import get_settings

settings = get_settings()

# -------------------------
# Async SQLAlchemy engine
# -------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=10,
    future=True,
)

# -------------------------
# Async session factory
# -------------------------
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# -------------------------
# FastAPI dependency
# -------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a transactional scope around a series of database operations.

    Yields
    ------
    AsyncSession
        An async SQLAlchemy session instance.
    """
    async with async_session_factory() as session:
        yield session
