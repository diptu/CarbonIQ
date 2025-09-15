# ruff: noqa: D401
"""Database connectivity health service."""

from __future__ import annotations

import logging

from ima_service.app.core.config import get_settings

from ..schemas import HealthCheckResponse
from .base import run_check
from .helpers import parse_pg_uri, ssl_enabled

LOG = logging.getLogger(__name__)


async def database_health_service() -> HealthCheckResponse:
    """Return database connectivity status (503 on failure)."""
    async def _check() -> bool:
        try:
            settings = get_settings()
        except Exception as exc:  # pragma: no cover
            LOG.warning("DB settings unavailable: %s", exc)
            return False

        try:
            import asyncpg  # type: ignore[import-not-found]
        except Exception as exc:  # pragma: no cover
            LOG.warning("asyncpg import failed: %s", exc)
            return False

        try:
            params = parse_pg_uri(settings.database.uri)
            params["ssl"] = ssl_enabled(settings.database.ssl_mode)
            conn = await asyncpg.connect(**params)
            try:
                await conn.execute("SELECT 1")
            finally:
                await conn.close()
            return True
        except Exception as exc:
            LOG.warning("DB health error: %s", exc)
            return False

    return await run_check(
        "Database", _check, details_key="database", timeout=2.5
    )
