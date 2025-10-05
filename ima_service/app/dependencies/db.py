# app/dependencies/db.py
"""Database session dependency for FastAPI endpoints."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a transactional scope around a series of operations.

    Yields
    ------
    AsyncSession
        Async SQLAlchemy session for DB operations.
    """
    async with async_session() as session:
        yield session
