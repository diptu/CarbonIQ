# FILE: ima_service/app/api/v1/health/services/database.py
"""
Database connectivity health service (SELECT 1).
"""

from __future__ import annotations

from sqlalchemy import text

from ima_service.app.db.session import get_session_manager

from ..schemas import HealthCheckResponse
from .base import LOG, RESET, YELLOW, run_check


async def _check_database() -> bool:
    """Return True if `SELECT 1` succeeds; exceptions bubble to the runner."""
    try:
        manager = get_session_manager()
        async with manager.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # pylint: disable=broad-except
        # warning for transient, error for hard issues can be tuned here
        LOG.warning(
            "%sDatabase%s connectivity check failed: %s", YELLOW, RESET, exc
        )
        return False


async def database_health_service() -> HealthCheckResponse:
    """Public service wrapper for database health."""
    return await run_check(
        "Database", _check_database, timeout=2.0, key="database"
    )
