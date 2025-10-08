"""Async SQLAlchemy session and engine setup for FastAPI."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import get_settings

# -------------------------
# Settings
# -------------------------
settings = get_settings()

# -------------------------
# Async engine
# -------------------------
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,  # SQLAlchemy 2.0 style
)

# -------------------------
# Async session factory
# -------------------------
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# -------------------------
# FastAPI dependency
# -------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional async session for request scope.

    Yields
    ------
    AsyncSession
        SQLAlchemy async session instance.
    """
    async with async_session() as session:
        yield session
