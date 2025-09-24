"""
Expose all route modules for API v2.

Import and register your v2 route modules here.
"""

from fastapi import APIRouter
from . import example

api_router = APIRouter()

# Include route modules
api_router.include_router(example.router, prefix="/example", tags=["example"])
