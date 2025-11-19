# gateway_service/app/api/v1/routes/users.py
"""Gateway proxy for all /users endpoints — forwards requests to user_service."""

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
    Supports GET, POST, PUT, DELETE automatically.
    """
    try:
        url = f"{USER_BASE}{path}"
        print(f"Hitting user service URL: {url}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            request_headers = headers or {}
            method_upper = method.upper()
            if method_upper == "POST":
                resp = await client.post(url, json=payload, headers=request_headers)
            elif method_upper == "GET":
                resp = await client.get(url, params=params, headers=request_headers)
            elif method_upper == "PUT":
                resp = await client.put(url, json=payload, headers=request_headers)
            elif method_upper == "DELETE":
                resp = await client.delete(url, headers=request_headers)
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
async def list_users(request: Request, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
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
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(f"/users/{user_id}", method="GET", headers=headers)


# ---------------------
# Create user
# ---------------------
@router.post(
    "",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def create_user(request: Request, payload: dict):
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(
        "/users/", payload=payload, method="POST", headers=headers
    )


# ---------------------
# Update user
# ---------------------
@router.put(
    "/{user_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def update_user(user_id: str, request: Request, payload: dict):
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(
        f"/users/{user_id}", payload=payload, method="PUT", headers=headers
    )


# ---------------------
# Delete user
# ---------------------
@router.delete(
    "/{user_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def delete_user(user_id: str, request: Request):
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(f"/users/{user_id}", method="DELETE", headers=headers)


# ---------------------
# Activate user
# ---------------------
@router.post(
    "/{user_id}/activate",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def activate_user(user_id: str, request: Request):
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(
        f"/users/{user_id}/activate", method="POST", headers=headers
    )


# ---------------------
# Deactivate user
# ---------------------
@router.post(
    "/{user_id}/deactivate",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def deactivate_user(user_id: str, request: Request):
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(
        f"/users/{user_id}/deactivate", method="POST", headers=headers
    )


# ---------------------
# Verify user (login)
# ---------------------
@router.post(
    "/verify",
    response_model=APIResponse,
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def verify_user(request: Request, payload: dict):
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(
        "/users/verify", payload=payload, method="POST", headers=headers
    )
