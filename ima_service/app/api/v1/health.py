"""Health endpoint (readiness/liveness)."""

from __future__ import annotations
from fastapi import APIRouter, Depends, status
from ...core.settings import Settings, get_settings
from ... import __version__

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health(st: Settings = Depends(get_settings)) -> dict[str, str]:
    return {
        "status": "ok",
        "service": st.app_name,
        "version": __version__,
        "env": st.env,
    }
