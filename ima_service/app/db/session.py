# app/db/session.py
"""Async SQLAlchemy session and engine setup."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()

# Async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in dev
    future=True,
)

# Async session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency for FastAPI
async def get_db() -> AsyncSession:
    """Provide a transactional scope around a series of operations."""
    async with async_session() as session:
        yield session
