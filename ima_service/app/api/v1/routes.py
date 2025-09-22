"""API v1 aggregator: health, auth, users, secure."""

from __future__ import annotations
from fastapi import APIRouter
from .health import router as health_router
from .auth import router as auth_router
from .users.routes import router as users_router
from .secure import router as secure_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(secure_router)

__all__ = ["router"]
