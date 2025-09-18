# FILE: ima_service/app/main.py
"""
FastAPI application setup with structured logging and clean startup/shutdown.

- Single module-level `app`.
- Startup logs include DB connection hints (non-sensitive).
- Graceful shutdown of Redis and SQLAlchemy engine.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError  # third-party before first-party

from ima_service.app.api.v1 import v1_router
from ima_service.app.core import (
    RedisClientError,
    close_redis_client,
    get_redis_client,
    get_settings,
    setup_logging,
)
from ima_service.app.core.config import Settings
from ima_service.app.db.session import AsyncSessionManager, get_session_manager

LOG = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """
    App lifespan: configure logging, emit startup diagnostics, cleanly shutdown.
    The FastAPI instance is unused here; name it `_` to avoid lint warnings.
    """
    # ---- Startup -----------------------------------------------------------
    settings: Settings = get_settings()
    setup_logging(debug=settings.debug)

    # Read DB fields via getattr to avoid pylint false-positives
    # on Pydantic models.
    db_ssl_mode = getattr(settings.database, "ssl_mode", None)
    db_effective_uri = getattr(settings.database, "effective_uri", "")

    LOG.info(
        "app_startup",
        extra={
            "app_name": settings.app_name,
            "env": settings.env,
            "db_ssl_mode": db_ssl_mode,
            # Avoid logging credentials; only note if a URI is configured
            "db_uri_set": bool(db_effective_uri),
        },
    )

    # Optional: warm up Redis client (non-fatal if unavailable)
    try:
        get_redis_client()
    except RedisClientError as exc:  # pragma: no cover
        LOG.warning("redis_client_unavailable", extra={"error": str(exc)})

    # Hand control to the application
    yield

    # ---- Shutdown ----------------------------------------------------------
    # Close Redis
    try:
        await close_redis_client()
    except RedisClientError:  # pragma: no cover
        pass  # already closed or not initialized

    # Dispose SQLAlchemy engine
    try:
        manager: AsyncSessionManager = get_session_manager()
        await manager.dispose()
    except SQLAlchemyError as exc:  # pragma: no cover
        LOG.warning("db_engine_dispose_failed", extra={"error": str(exc)})


# Single module-level app (no redefinition)
app = FastAPI(title=get_settings().app_name, version="1.0.0", lifespan=lifespan)
app.include_router(v1_router)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Simple root route for quick smoke checks."""
    return {"status": "ok"}
