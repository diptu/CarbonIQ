# app/dependencies/db.py
"""Database session dependency using SQLAlchemy Async.

Provides:
- Async session per request
- Automatic rollback on exception
- Tenant-aware schema enforcement
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async SQLAlchemy session and handle commit/rollback.

    Yields
    ------
    AsyncSession
        SQLAlchemy async session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_tenant_db(
    schema_name: Optional[str] = None,
) -> AsyncGenerator[AsyncSession, None]:
    """Yield a tenant-specific async DB session.

    Args
    ----
    schema_name : Optional[str]
        Schema for multi-tenant isolation

    Yields
    ------
    AsyncSession
        Scoped async SQLAlchemy session
    """
    async with AsyncSessionLocal() as session:
        if schema_name:
            # use sqlalchemy.text for safety
            await session.execute(
                text("SET search_path TO :schema").bindparams(schema=schema_name)
            )
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
