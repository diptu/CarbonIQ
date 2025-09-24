# app/api/deps.py
"""
Shared dependencies for FastAPI routes.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from ima_service.app.db.session import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that yields a database session.
    """
    async with async_session_maker() as session:
        yield session
