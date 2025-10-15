# ima_service/app/dependency/db.py

from typing import AsyncGenerator
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency wrapper around core get_db() for FastAPI routes.

    Handles commit/rollback automatically.
    """
    async for session in get_db():  # <- use async for instead of async with
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
