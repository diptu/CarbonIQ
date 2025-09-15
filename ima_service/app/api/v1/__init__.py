"""API v1 package: re-export FastAPI router for inclusion."""

from fastapi import APIRouter

from ima_service.app.api.v1.health.router import router as health_router

v1_router = APIRouter()
v1_router.include_router(health_router)

__all__ = ["v1_router"]
