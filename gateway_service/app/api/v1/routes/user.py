# gateway_service/app/api/v1/routes/users.py
"""Lightweight proxy routes for /users endpoints — all logic handled by user_service."""

from typing import Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from gateway_service.app.core.config import settings
from shared_service.app.core.deps import require_permissions
from shared_service.app.utils.response import APIResponse

router = APIRouter(prefix="/users", tags=["users"])

# Base URL for the user service (running at port 8000)
USER_BASE = settings.USER_SERVICE_URL  # e.g., "http://127.0.0.1:8000"


async def _forward_to_user_service(
    path: str,
    payload: Optional[Dict] = None,
    params: Optional[Dict] = None,
    method: str = "GET",
    headers: Optional[Dict] = None,
) -> JSONResponse:
    """
    Forward request to user_service and return its response.
    Supports GET and POST requests automatically.
    """
    try:
        url = f"{USER_BASE}{path}"
        print(f"Hitting user service URL: {url}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            request_headers = headers or {}
            if method.upper() == "POST":
                resp = await client.post(url, json=payload, headers=request_headers)
            elif method.upper() == "GET":
                resp = await client.get(url, params=params, headers=request_headers)
            else:
                raise HTTPException(
                    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                    detail=f"Method {method} not supported",
                )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"User service unavailable: {exc}",
        )

    try:
        data = resp.json()
    except ValueError:
        data = {"detail": resp.text}

    return JSONResponse(content=data, status_code=resp.status_code)


# ---------------------
# List users
# ---------------------
@router.get(
    "",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def list_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
):
    """Proxy GET /users request to user_service."""
    params = {"skip": skip, "limit": limit}
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service("/users/", params=params, method="GET", headers=headers)


# ---------------------
# Get single user
# ---------------------
@router.get(
    "/{user_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def get_user(user_id: str, request: Request):
    """Proxy GET /users/{user_id} request to user_service."""
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(f"/users/{user_id}", method="GET", headers=headers)
