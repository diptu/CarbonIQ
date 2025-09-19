# FILE: ima_service/app/api/v1/__init__.py
"""
API v1 package root.

Aggregates all versioned routers into a single APIRouter
for inclusion in the FastAPI app.
"""

from __future__ import annotations

from fastapi import APIRouter

from .health import router as health_router
from .users import router as users_router

v1_router = APIRouter(prefix="/v1")

# Health check endpoints
v1_router.include_router(health_router)

# User-related endpoints
v1_router.include_router(users_router)

__all__ = ["v1_router"]
