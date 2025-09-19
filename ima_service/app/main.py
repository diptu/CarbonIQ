# FILE: ima_service/app/main.py
"""
FastAPI application factory and module-level `app`.

- Uses project settings and structured logging.
- Mounts all v1 routers under `/v1`.
"""

from __future__ import annotations

from fastapi import FastAPI

from ima_service.app.api.v1 import v1_router
from ima_service.app.core import get_settings, setup_logging


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    setup_logging(debug=settings.debug)

    application = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Routers
    application.include_router(v1_router, prefix="")

    # # Simple root route for quick sanity checks
    # @application.get("/", tags=["meta"])
    # async def root() -> dict[str, str]:
    #     return {"status": "ok", "service": settings.app_name}

    return application


# Uvicorn/ASGI entrypoint
app: FastAPI = create_app()
