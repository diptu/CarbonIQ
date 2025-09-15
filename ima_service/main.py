"""
FILE : ima_service / main.py
Entry point for the IMA FastAPI service (no container).

Reads configuration from `app.core.config.Settings` (Pydantic BaseSettings)
and boots uvicorn.

- Exposes module-level `app` so this works:
    uvicorn ima_service.main:app --reload
- Or run as a module:
    python -m ima_service.main
"""

from __future__ import annotations

from typing import Literal
from urllib.parse import urlparse

import uvicorn

from ima_service.app.core.config import get_settings
from ima_service.app.main import create_app

# Export ASGI application for uvicorn discovery (`ima_service.main:app`)
app = create_app()

__all__ = ["app", "run"]


def _host_from_base_url(base_url: str) -> str:
    """Extract host from a base URL; default to 127.0.0.1 if missing."""
    parsed = urlparse(base_url)
    return parsed.hostname or "127.0.0.1"


def _log_level(debug: bool) -> Literal["critical", "error",
                                       "warning", "info", "debug"]:
    """Map debug flag to a uvicorn log level."""
    return "debug" if debug else "info"


def run() -> None:
    """Start uvicorn with configuration derived from settings.

    Notes
    -----
    - `settings.debug` controls both `reload` and `log_level`.
    - Host is derived from `settings.base_url`.
    """
    settings = get_settings()

    host = _host_from_base_url(settings.base_url)
    port = settings.port
    log_level = _log_level(settings.debug)

    # Single worker keeps dev reload predictable.
    workers = 1 if settings.debug else 1

    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        reload=settings.debug,
        log_level=log_level,
        workers=workers,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
    server = uvicorn.Server(config)
    server.run()


if __name__ == "__main__":
    run()
