# app/dependencies/db.py
"""Database session dependency for FastAPI endpoints."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session
from app.services.base_service import BaseService


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a transactional scope around a series of operations.

    Yields
    ------
    AsyncSession
        Async SQLAlchemy session for DB operations.
    """
    async with async_session() as session:
        try:
            BaseService.log_action(action="db_session_start")
            yield session
            await session.commit()
            BaseService.log_action(action="db_session_commit")
        except Exception as e:
            await session.rollback()
            BaseService.log_action(
                action="db_session_rollback", details={"error": str(e)}
            )
            raise
        finally:
            BaseService.log_action(action="db_session_end")
