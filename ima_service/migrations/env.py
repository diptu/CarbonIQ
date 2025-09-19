# FILE: ima_service/migrations/env.py
"""Alembic environment configuration (async-aware, service-root).

- Loads DB URL from ima_service.app.core.config.get_settings()
- Adds repo root to sys.path so `ima_service` imports resolve
- Supports both async and sync drivers
- Filters out sqlalchemy.url from kwargs to avoid duplicate 'url' errors
"""

from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path
from typing import Any, Dict

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

# -------------------------------------------------------------------
# Ensure the repository root is on sys.path (…/CarbonIQ)
# env.py is at …/ima_service/migrations/env.py
# parents[0] = migrations/, [1] = ima_service/, [2] = repo root
# -------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# Import app metadata & settings AFTER sys.path fix
from ima_service.app.db.base import Base  # noqa: E402
from ima_service.app.core.config import get_settings  # noqa: E402

# Alembic Config object (provides access to values in alembic.ini)
config = context.config

# Inject URL from app settings (overrides alembic.ini if present)
_settings = get_settings()
_DB_URL = _settings.database.effective_uri
config.set_main_option("sqlalchemy.url", _DB_URL)

# Configure logging from alembic.ini, if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate
target_metadata = Base.metadata


def _is_async_driver(url: str) -> bool:
    """Heuristic for async drivers."""
    return (
        "+asyncpg" in url
        or "+aiosqlite" in url
        or url.startswith("sqlite+aiosqlite")
        or url.startswith("postgresql+asyncpg")
    )


def _engine_kwargs_from_ini() -> Dict[str, Any]:
    """Extract engine kwargs from alembic.ini, sans 'sqlalchemy.url'."""
    section = config.get_section(config.config_ini_section, {}) or {}
    out: Dict[str, Any] = {}
    for k, v in section.items():
        if not k.startswith("sqlalchemy."):
            continue
        if k == "sqlalchemy.url":
            continue  # avoid passing URL twice
        out[k[len("sqlalchemy.") :]] = v
    return out


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DBAPI/engine)."""
    context.configure(
        url=_DB_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        # If using SQLite and need batch mode:
        # render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def _configure_and_run(connection: Connection) -> None:
    """Configure Alembic on a sync Connection and run migrations.

    NOTE: This MUST accept a Connection because async_engine.run_sync(...)
    passes the sync connection as the first positional argument.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def _run_async_migrations(async_engine: AsyncEngine) -> None:
    """Run migrations using an async Engine (DDL executed via sync conn)."""
    async with async_engine.connect() as async_conn:
        await async_conn.run_sync(_configure_and_run)


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    url = _DB_URL
    ekw = _engine_kwargs_from_ini()

    if _is_async_driver(url):
        # Async engine path
        async_engine = create_async_engine(url, poolclass=pool.NullPool, **ekw)
        try:
            asyncio.run(_run_async_migrations(async_engine))
        finally:
            dispose = async_engine.dispose()
            # handle both sync and awaitable dispose implementations
            if hasattr(dispose, "__await__"):
                asyncio.run(dispose)  # type: ignore[arg-type]
    else:
        # Sync engine path
        connectable = create_engine(url, poolclass=pool.NullPool, **ekw)
        with connectable.connect() as connection:
            _configure_and_run(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
