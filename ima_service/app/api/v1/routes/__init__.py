"""API v1 routes package."""

from fastapi import APIRouter

from . import user, role, auth, health

router = APIRouter()
router.include_router(user.router)
router.include_router(role.router)
router.include_router(auth.router)
router.include_router(health.router)
