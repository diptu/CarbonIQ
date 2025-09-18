# FILE: ima_service/app/api/__init__.py
"""
API package root.

This module aggregates all API version routers into a single `api_router`.

Usage
-----
from ima_service.app.api import api_router
app.include_router(api_router)
"""

from __future__ import annotations

from fastapi import APIRouter

from .v1 import v1_router

# pylint: disable=invalid-name
api_router = APIRouter()
api_router.include_router(v1_router)

__all__ = ["api_router"]
