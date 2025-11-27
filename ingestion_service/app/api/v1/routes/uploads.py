# app/api/v1/routes/uploads.py
import logging

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from ingestion_service.app.crud import uploads as uploads_crud
from ingestion_service.app.db.session import get_db
from ingestion_service.app.schemas.uploads import UploadMetaOut
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/uploads", tags=["uploads"])

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.post("/", response_model=UploadMetaOut, status_code=201)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a file, save metadata to DB, cache, and enqueue background job.

    Handles:
    - 400 if file exceeds MAX_FILE_SIZE
    - 500 for unexpected server errors
    """
    try:
        meta = await uploads_crud.create_upload(file, db)

        # Enqueue background processing
        background_tasks.add_task(uploads_crud.enqueue_upload_job, meta["id"], meta)

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
async def get_upload(file_id: str, db: AsyncSession = Depends(get_db)):
    """
    Retrieve upload metadata (Redis cache first, DB fallback).

    Handles:
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
