import logging
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from ingestion_service.app.core.redis import get_redis_client  # your DI for Redis
from ingestion_service.app.crud import uploads as uploads_crud
from ingestion_service.app.db.session import get_db
from ingestion_service.app.schemas.uploads import UploadMetaOut
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/uploads", tags=["uploads"])

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# -------------------------------
# Routes
# -------------------------------


@router.post("/", response_model=UploadMetaOut, status_code=201)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    redis_client: Optional[Any] = Depends(get_redis_client),
):
    """
    Upload a file asynchronously:
    - Streams file to disk with size validation
    - Persists metadata in DB
    - Fire-and-forget cache & enqueue via BackgroundTasks

    Handles:
    - 400 if file exceeds MAX_FILE_SIZE
    - 500 for unexpected server errors
    """
    try:
        meta = await uploads_crud.create_upload(file, db, redis_client)

        # Fire-and-forget background tasks for caching and enqueuing
        if redis_client:
            background_tasks.add_task(
                uploads_crud.cache_upload_metadata, redis_client, meta["id"], meta
            )
            background_tasks.add_task(
                uploads_crud.enqueue_upload_job, redis_client, meta["id"], meta
            )

        return meta

    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error during file upload")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while uploading the file.",
        )


@router.get("/{file_id}", response_model=UploadMetaOut)
async def get_upload(
    file_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve upload metadata:
    - Returns Path object for `path` key
    - 404 if file not found
    - 500 for unexpected server errors
    """
    try:
        meta = await uploads_crud.get_upload(file_id, db)
        return meta

    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error fetching upload metadata")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving the file metadata.",
        )
