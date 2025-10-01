"""Health check endpoint with standardized APIResponse."""

from fastapi import APIRouter, status
from pydantic import create_model

from app.schemas.base import APIResponse

router = APIRouter(prefix="/health", tags=["health"])

# ----------------------
# Concrete response model for OpenAPI
# ----------------------
HealthResponse = create_model(
    "HealthResponse", __base__=APIResponse, details=(dict, ...)
)


# ----------------------
# Health Check
# ----------------------
@router.get(
    "/",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Check service health",
    description=(
        "Perform a simple health check to confirm \
        that the service is up and running.\n\n"
        "- Returns 200 OK if the service is healthy.\n"
        "- `details` field contains a simple `status` key."
    ),
)
async def health_check():
    """Simple health check with standardized response."""
    return HealthResponse(
        statusCode=status.HTTP_200_OK,
        msg="Service is healthy",
        details={"status": "ok"},
    )
