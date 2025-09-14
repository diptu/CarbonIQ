"""FastAPI application entrypoint for ima_service."""

from __future__ import annotations

from fastapi import FastAPI

from ima_service.app.api.v1 import v1_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(title="ima_service")
    application.include_router(v1_router)
    return application


app = create_app()
