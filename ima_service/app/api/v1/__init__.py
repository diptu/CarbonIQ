# FILE: ima_service/app/api/v1/__init__.py
"""
API v1 package root.
"""

from __future__ import annotations

from fastapi import APIRouter

from .health import router as _health_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(_health_router)

__all__ = ["v1_router"]
