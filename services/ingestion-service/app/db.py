"""Async SQLAlchemy engine/session setup."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, echo=settings.database_echo)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models in this service."""


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a request-scoped async session."""
    async with AsyncSessionLocal() as session:
        yield session
