# FILE: ima_service/app/api/v1/health/services/helpers.py
"""
Helper utilities used by health services.
"""

from __future__ import annotations

from urllib.parse import unquote, urlparse


def ssl_enabled(mode: str | None) -> bool:
    """Return True if DB TLS should be enabled given a mode string."""
    if mode is None:
        return True
    return mode.strip().lower() not in {"", "disable", "off", "false", "0"}


def parse_pg_uri(uri: str) -> dict[str, object]:
    """Parse a SQLAlchemy Postgres DSN into discrete parts."""
    clean = uri.replace("+asyncpg", "", 1)
    u = urlparse(clean)
    return {
        "user": unquote(u.username or ""),
        "password": unquote(u.password or ""),
        "host": u.hostname or "localhost",
        "port": u.port or 5432,
        "database": (u.path.lstrip("/") or None),
    }
