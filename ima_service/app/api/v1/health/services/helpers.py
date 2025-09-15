# ruff: noqa: D401
"""Small helper utilities used by health services."""

from __future__ import annotations

from urllib.parse import unquote, urlparse


def ssl_enabled(mode: str | None) -> bool:
    """Return True if DB TLS should be enabled."""
    if mode is None:
        return True
    v = mode.strip().lower()
    return v not in {"", "disable", "off", "false", "0"}


def parse_pg_uri(uri: str) -> dict[str, object]:
    """Parse a SQLAlchemy DSN into asyncpg kwargs."""
    clean = uri.replace("+asyncpg", "", 1)
    u = urlparse(clean)
    return {
        "user": unquote(u.username or ""),
        "password": unquote(u.password or ""),
        "host": u.hostname or "localhost",
        "port": u.port or 5432,
        "database": (u.path.lstrip("/") or None),
    }
