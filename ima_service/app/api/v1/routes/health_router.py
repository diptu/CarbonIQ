# ima_service/app/v1/routes/health_router.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db  # type: ignore
from app.api.v1.docs import health_docs
from ima_service.app.schemas.auth import APIResponse  # Import the doc strings

router = APIRouter()


@router.get("/server", **health_docs.SERVER_HEALTH)
async def server_health_check():
    """Health check for server availability."""
    return APIResponse(data={"status": "ok"}).model_dump()


@router.get("/db", **health_docs.DB_HEALTH)
async def db_health_check(db: AsyncSession = Depends(get_db)):
    """Health check for DB connectivity."""
    try:
        # Use async context manager correctly
        async with db as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database unreachable: {e}")

    return APIResponse(data={"status": "ok", "database": "connected"}).model_dump()
