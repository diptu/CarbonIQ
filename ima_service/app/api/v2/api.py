"""
API v2 router aggregator.

This file serves as the entry point for version 2 of the API.
Initially, it may just expose a simple healthcheck route,
but you can extend it with new routes as v2 evolves.
"""

from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/health", tags=["health"])
async def health_check():
    """
    Basic health check endpoint for API v2.
    """
    return {"status": "ok", "version": "v2"}
