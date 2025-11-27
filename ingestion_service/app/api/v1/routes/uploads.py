import logging
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from ingestion_service.app.core.config import settings
from ingestion_service.app.core.redis import get_redis_client
from ingestion_service.app.crud import uploads as uploads_crud
from ingestion_service.app.db.session import get_db
from ingestion_service.app.schemas.uploads import UploadMetaOut
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/uploads", tags=["uploads"])
logger = logging.getLogger(__name__)


# -------------------------------------
# POST /uploads
# -------------------------------------
@router.post("/", response_model=UploadMetaOut, status_code=201)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    redis_client: Optional[Any] = Depends(get_redis_client),
):
    try:
        file_id = str(uuid.uuid4())
        ext = Path(file.filename).suffix
        dest_filename = f"{file_id}{ext}"
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        dest_path = upload_dir / dest_filename

        # -----------------
        # Save temp copy immediately (so UploadFile can be closed safely)
        # -----------------
        tmp_path = Path(tempfile.gettempdir()) / f"{file_id}{ext}"
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # -----------------
        # Save to final destination asynchronously
        # -----------------
        size = await uploads_crud.save_file_from_path(tmp_path, dest_path)

        # -----------------
        # Persist metadata
        # -----------------
        meta = await uploads_crud.save_upload_metadata(
            file_id, file.filename, file.content_type, size, dest_path, db
        )

        # -----------------
        # Background tasks: cache & enqueue
        # -----------------
        if redis_client:
            background_tasks.add_task(
                uploads_crud.cache_upload_metadata, redis_client, file_id, meta
            )
            background_tasks.add_task(uploads_crud.enqueue_upload_job, redis_client, file_id, meta)

        return meta

    except Exception as e:
        logger.exception(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error while uploading file.")


# -------------------------------------
# GET /uploads/{file_id}
# -------------------------------------
@router.get("/{file_id}", response_model=UploadMetaOut)
async def get_upload(file_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await uploads_crud.get_upload(file_id, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Get upload failed: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error fetching upload metadata.")
