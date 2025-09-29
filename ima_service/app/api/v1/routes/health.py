"""Health check endpoint with standardized APIResponse."""

from fastapi import APIRouter
from pydantic import create_model

from app.schemas.base import APIResponse

router = APIRouter(prefix="/health", tags=["health"])

# ----------------------
# Concrete response model for OpenAPI
# ----------------------
HealthResponse = create_model(
    "HealthResponse", __base__=APIResponse, details=(dict, ...)
)


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Simple health check with standardized response."""
    return HealthResponse(
        statusCode=200,
        msg="Service is healthy",
        details={"status": "ok"},
    )
