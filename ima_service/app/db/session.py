"""Async SQLAlchemy session and engine setup."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import get_settings

settings = get_settings()

# Async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# Async session factory
async_session = sessionmaker(  # type:ignore[call-overload]
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope around a series of operations."""
    async with async_session() as session:
        yield session
