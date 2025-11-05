# gateway_service/app/api/v1/routes/auth.py
"""Lightweight proxy routes for /auth endpoints — all logic handled by auth_service."""

from typing import Any

import httpx
from auth_service.app.schemas.auth import LoginRequest, RefreshRequest
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from gateway_service.app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

AUTH_BASE = settings.AUTH_SERVICE_URL


async def _forward_to_auth_service(path: str, payload: dict) -> JSONResponse:
    """Utility to forward any auth request to auth_service and return its response."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{AUTH_BASE}{path}", json=payload)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth service unavailable: {exc}",
        )

    try:
        data = resp.json()
    except ValueError:
        data = {"detail": resp.text}

    return JSONResponse(content=data, status_code=resp.status_code)


@router.post("/login")
async def login(payload: LoginRequest) -> Any:
    """Proxy /auth/login request to auth_service."""
    return await _forward_to_auth_service("/auth/login", payload.dict())


@router.post("/refresh")
async def refresh(payload: RefreshRequest) -> Any:
    """Proxy /auth/refresh request to auth_service."""
    return await _forward_to_auth_service("/auth/refresh", payload.dict())


@router.post("/logout")
async def logout(payload: RefreshRequest) -> Any:
    """Proxy /auth/logout request to auth_service."""
    return await _forward_to_auth_service("/auth/logout", payload.dict())
