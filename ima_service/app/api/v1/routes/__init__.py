# api/v1/routes/__init__.py
"""API v1 routes package."""

from fastapi import APIRouter

from . import auth, health, role, user

router = APIRouter()
router.include_router(health.router)
router.include_router(user.router)
router.include_router(auth.router)
router.include_router(role.router)
