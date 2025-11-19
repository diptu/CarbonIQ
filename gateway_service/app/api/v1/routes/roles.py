# gateway_service/app/api/v1/routes/roles.py
"""Lightweight proxy routes for /roles endpoints — all logic handled by user_service."""

from typing import Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from gateway_service.app.core.config import settings
from shared_service.app.core.deps import require_permissions
from shared_service.app.utils.response import APIResponse

router = APIRouter(prefix="/roles", tags=["roles"])

# Base URL for the user service (running at port 8000)
USER_SERVICE_URL = settings.USER_SERVICE_URL  # e.g., "http://127.0.0.1:8000"


async def _forward_to_user_service(
    path: str,
    payload: Optional[Dict] = None,
    params: Optional[Dict] = None,
    method: str = "GET",
    headers: Optional[Dict] = None,
) -> JSONResponse:
    """Forward request to user_service and return its response."""
    url = f"{USER_SERVICE_URL}{path}"
    print(f"Hitting user service URL: {url}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            request_headers = headers or {}
            if method.upper() == "POST":
                resp = await client.post(url, json=payload, headers=request_headers)
            elif method.upper() == "GET":
                resp = await client.get(url, params=params, headers=request_headers)
            elif method.upper() == "PUT":
                resp = await client.put(url, json=payload, headers=request_headers)
            elif method.upper() == "DELETE":
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
# List Roles
# ---------------------
@router.get(
    "",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def list_roles(request: Request, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1)):
    """Proxy GET /roles to user_service."""
    params = {"skip": skip, "limit": limit}
    headers = {"Authorization": request.headers.get("Authorization")}
    # remove trailing slash to match user_service path
    return await _forward_to_user_service("/roles/", params=params, method="GET", headers=headers)


# ---------------------
# Get single role
# ---------------------
@router.get(
    "/{role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def get_role(role_id: str, request: Request):
    """Proxy GET /roles/{role_id} to user_service."""
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(f"/roles/{role_id}", method="GET", headers=headers)


# ---------------------
# Create Role
# ---------------------
@router.post(
    "",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def create_role(request: Request, payload: Dict):
    """Proxy POST /roles to user_service."""
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(
        "/roles/", payload=payload, method="POST", headers=headers
    )


# ---------------------
# Update Role
# ---------------------
@router.put(
    "/{role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def update_role(role_id: str, request: Request, payload: Dict):
    """Proxy PUT /roles/{role_id} to user_service."""
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(
        f"/roles/{role_id}", payload=payload, method="PUT", headers=headers
    )


# ---------------------
# Delete Role
# ---------------------
@router.delete(
    "/{role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def delete_role(role_id: str, request: Request):
    """Proxy DELETE /roles/{role_id} to user_service."""
    headers = {"Authorization": request.headers.get("Authorization")}
    return await _forward_to_user_service(f"/roles/{role_id}", method="DELETE", headers=headers)
