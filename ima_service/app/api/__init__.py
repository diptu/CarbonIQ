"""
app.api.__init__.py
API package (v1, v2).
API package initializer
- Imports and exposes all routers
- Allows main.py to just include the API module
"""

from fastapi import APIRouter

# Import routers from v1
from .v1.routes import (
    auth_router,
    # billing_router,
    permission_router,
    reporting_router,
    role_router,
    user_router,
)

# Create a main router to include all sub-routers
api_router = APIRouter()

# Include individual routers
api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])
api_router.include_router(user_router.router, prefix="/users", tags=["users"])
api_router.include_router(role_router.router, prefix="/roles", tags=["roles"])
api_router.include_router(
    permission_router.router, prefix="/permissions", tags=["permissions"]
)
api_router.include_router(reporting_router.router, prefix="/reports", tags=["reports"])
# api_router.include_router(billing_router.router, prefix="/billing", tags=["bills"])
