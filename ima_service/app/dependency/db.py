# ima_service/app/dependency/db.py
"""Database dependency for FastAPI routes."""

from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory  # type:ignore[import-not-found]


async def get_async_db() -> AsyncIterator[AsyncSession]:
    """Provide an async SQLAlchemy session for route dependencies."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
