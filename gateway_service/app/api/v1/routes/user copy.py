"""Lightweight proxy routes for /users endpoints — forwards requests with JWT validation."""

import logging
from typing import Any, Dict, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from gateway_service.app.core.config import settings
from shared_service.app.core.deps import get_cached_current_user, require_permissions
from sqlalchemy.orm import Session
from user_service.app.db.session import get_db
from user_service.app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])
USER_BASE = settings.USER_SERVICE_URL

# -------------------------------------------------------------------------
# Logging Setup
# -------------------------------------------------------------------------
logger = logging.getLogger("gateway.users")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)


# -------------------------------------------------------------------------
# Forwarding Helper
# -------------------------------------------------------------------------
async def _forward_to_user_service(
    path: str,
    method: str = "get",
    payload: Optional[Dict] = None,
    query: Optional[Dict] = None,
    headers: Optional[Dict] = None,
) -> JSONResponse:
    url = f"{USER_BASE}{path}"
    payload = payload or {}
    query = query or {}
    headers = headers or {}

    logger.debug(f"Forwarding request → {method.upper()} {url} | payload={payload} | query={query}")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if method == "post":
                resp = await client.post(url, json=payload, headers=headers)
            elif method == "get":
                resp = await client.get(url, params=query, headers=headers)
            elif method == "put":
                resp = await client.put(url, json=payload, headers=headers)
            elif method == "delete":
                if payload:
                    resp = await client.delete(url, json=payload, headers=headers)
                else:
                    resp = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method {method}")

    except httpx.RequestError as exc:
        logger.error(f"User service unavailable: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"User service unavailable: {exc}",
        )

    # parse JSON safely
    try:
        data = resp.json()
    except ValueError:
        data = {"detail": resp.text}

    logger.debug(f"Response ← status={resp.status_code}, body={str(data)[:400]}")

    # Return full response from user service to match its structure
    return JSONResponse(content=data, status_code=resp.status_code)


# -------------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------------
@router.get(
    "/",
    dependencies=[Depends(require_permissions(["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def list_users(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
) -> Any:
    """Proxy: List users (GET /users)."""
    headers = {"Authorization": request.headers.get("Authorization")}
    logger.debug(f"list_users called by user_id={current_user.id}")
    return await _forward_to_user_service("/", method="get", headers=headers)


@router.post("/")
async def create_user(
    request: Request,
    payload: dict,
    current_user: User = Depends(get_cached_current_user),
) -> Any:
    """Proxy: Create new user (POST /users)."""
    headers = {"Authorization": request.headers.get("Authorization")}
    logger.debug(f"create_user called by user_id={current_user.id}, payload={payload}")
    return await _forward_to_user_service("/", method="post", payload=payload, headers=headers)


@router.get(
    "/{user_id}",
    dependencies=[Depends(require_permissions(["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def get_user(
    request: Request, user_id: str, current_user: User = Depends(get_cached_current_user)
) -> Any:
    """Proxy: Get user details (GET /users/{user_id})."""
    headers = {"Authorization": request.headers.get("Authorization")}
    logger.debug(f"get_user called by user_id={current_user.id}, target_user_id={user_id}")
    return await _forward_to_user_service(f"/{user_id}", method="get", headers=headers)


@router.put(
    "/{user_id}",
    dependencies=[Depends(require_permissions(["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def update_user(
    request: Request,
    user_id: str,
    payload: dict,
    current_user: User = Depends(get_cached_current_user),
) -> Any:
    """Proxy: Update user (PUT /users/{user_id})."""
    headers = {"Authorization": request.headers.get("Authorization")}
    logger.debug(
        f"update_user called by user_id={current_user.id}, target_user_id={user_id}, payload={payload}"
    )
    return await _forward_to_user_service(
        f"/{user_id}", method="put", payload=payload, headers=headers
    )


@router.delete(
    "/{user_id}",
    dependencies=[Depends(require_permissions(["user.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def delete_user(
    request: Request, user_id: str, current_user: User = Depends(get_cached_current_user)
) -> Any:
    """Proxy: Delete user (DELETE /users/{user_id})."""
    headers = {"Authorization": request.headers.get("Authorization")}
    logger.debug(f"delete_user called by user_id={current_user.id}, target_user_id={user_id}")
    return await _forward_to_user_service(f"/{user_id}", method="delete", headers=headers)
