# ima_service/app/v1/routes/health_router.py

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db  # type: ignore
from app.api.v1.docs import health_docs
from ima_service.app.schemas.auth import APIResponse  # Import the doc strings

router = APIRouter()


@router.get("/server", **health_docs.SERVER_HEALTH, response_model=APIResponse)
async def server_health_check():
    return APIResponse.success(data={"status": "ok"}, message="Server is healthy")


@router.get("/db", **health_docs.DB_HEALTH, response_model=APIResponse)
async def db_health_check(db: AsyncSession = Depends(get_db)):
    try:
        async with db as session:
            await session.execute(text("SELECT 1"))
    except Exception as e:
        return APIResponse.error(message=f"Database unreachable: {e}", status_code=500)

    return APIResponse.success(
        data={"status": "ok", "database": "connected"}, message="DB connected"
    )
