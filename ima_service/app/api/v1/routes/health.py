"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Simple health check."""
    return {"status": "ok"}
