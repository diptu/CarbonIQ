"""Dependency utilities for FastAPI endpoints."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session generator for dependency injection.
    Usage in routes: db: AsyncSession = Depends(get_db)
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
