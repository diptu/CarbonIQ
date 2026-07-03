"""Liveness/readiness endpoint. Not JWT-protected (used by orchestrators/LBs)."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.db import get_db

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    db_ok = True
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "service": settings.service_name,
        "database": "ok" if db_ok else "unreachable",
    }
