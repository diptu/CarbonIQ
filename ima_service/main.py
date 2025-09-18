# FILE : ima_service / main.py
"""
Entry point for the IMA FastAPI service (non-container run).

Expose module-level `app` so this works:
    uvicorn ima_service.main:app --reload
Or run as a module:
    python -m ima_service.main
"""

from __future__ import annotations

from typing import Literal
from urllib.parse import urlparse

import uvicorn

from ima_service.app.core.config import get_settings
from ima_service.app.main import create_app

# Public ASGI application for uvicorn discovery (`ima_service.main:app`)
app = create_app()

__all__ = ["app", "run"]

LogLevel = Literal["critical", "error", "warning", "info", "debug"]


def _host_from_url(base_url: str) -> str:
    """Return host extracted from base_url, defaulting to 127.0.0.1."""
    parsed = urlparse(base_url)
    return parsed.hostname or "127.0.0.1"


def _log_level(debug: bool) -> LogLevel:
    """Map debug flag to a uvicorn log level."""
    return "debug" if debug else "info"


def _workers(debug: bool) -> int:
    """Pick worker count; keep 1 in dev for reload predictability."""
    if debug:
        return 1
    # Allow optional `workers` in settings; default to 1 if absent.
    return int(getattr(get_settings(), "workers", 1))


def run() -> None:
    """Start uvicorn using settings-derived configuration."""
    settings = get_settings()
    host = _host_from_url(settings.base_url)
    port = settings.port
    level = _log_level(settings.debug)

    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        reload=settings.debug,
        log_level=level,
        workers=settings.workers if not settings.debug else 1,
        proxy_headers=True,
        forwarded_allow_ips="*",
        # Good defaults; keep access log on, respect lifespan from app.
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    run()
