"""
Example placeholder routes for API v2.

Replace or extend with actual endpoints.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Example root endpoint")
async def get_example():
    """Placeholder"""
    return {"message": "This is an example v2 endpoint"}
