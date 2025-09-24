# app/db/init_db.py
"""
Database initialization utilities for the IMA service.

This module provides helper functions to create the database schema and
optionally seed initial data (e.g., default users, roles).
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ima_service.app.db.base_class import Base  # imports all models via app.db.base
from ima_service.app.db.session import engine


async def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This should be called at application startup or from a migration script.
    """
    async with engine.begin() as conn:
        # Run schema creation
        await conn.run_sync(Base.metadata.create_all)


async def reset_db(session: AsyncSession) -> None:
    """
    Example utility: truncate all tables (useful in testing).
    """
    for table in reversed(Base.metadata.sorted_tables):
        await session.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))
    await session.commit()
