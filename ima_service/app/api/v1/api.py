# app/api/v1/api
"""
API v1 router aggregator.

This module collects and registers all API v1 route modules
into a single router that can be included in the main app.
"""

from fastapi import APIRouter
from ima_service.app.api.v1.routes import user

api_router = APIRouter()

# Register routes here
api_router.include_router(user.router, tags=["users"])
