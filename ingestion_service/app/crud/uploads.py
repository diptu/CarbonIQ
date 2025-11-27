import logging
import os
import uuid
from typing import Optional

from fastapi import HTTPException, UploadFile, status
from ingestion_service.app.core.config import settings
from ingestion_service.app.models.upload import Upload
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Redis client placeholder; initialize in main.py
redis = None


async def save_file_to_disk(file: UploadFile, dest_path: str) -> None:
    """Save UploadFile to disk asynchronously."""
    import aiofiles

    try:
        async with aiofiles.open(dest_path, "wb") as out_file:
            while chunk := await file.read(1024 * 64):  # 64 KB chunks
                await out_file.write(chunk)
        await file.close()
        logger.info(f"File saved to {dest_path}")
    except Exception as e:
        logger.exception(f"Failed to save file to disk: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File storage failed"
        )


async def save_upload_metadata(
    file_id: str, filename: str, content_type: str, size: int, path: str, db: AsyncSession
) -> dict:
    """Persist upload metadata to the database."""
    try:
        async with db.begin():
            stmt = insert(Upload).values(
                id=file_id,
                filename=filename,
                content_type=content_type,
                size=size,
                path=path,
            )
            await db.execute(stmt)
        logger.info(f"Upload metadata saved: {file_id}")
        return {
            "id": file_id,
            "filename": filename,
            "content_type": content_type,
            "size": size,
            "path": path,
        }
    except Exception as e:
        logger.exception(f"Failed to persist upload metadata: {e}")
        raise


async def cache_upload_metadata(file_id: str, meta: dict, expire_seconds: int = 3600) -> None:
    """Cache upload metadata in Redis (best-effort)."""
    if redis:
        try:
            await redis.set(f"upload:meta:{file_id}", str(meta), ex=expire_seconds)
        except Exception as e:
            logger.warning(f"Failed to cache metadata in Redis: {e}")


async def enqueue_upload_job(file_id: str, meta: dict) -> None:
    """Push a job to Redis queue for downstream processing (best-effort)."""
    if redis:
        try:
            await redis.rpush("ingest:queue", str({"file_id": file_id, "meta": meta}))
        except Exception as e:
            logger.warning(f"Failed to enqueue background job: {e}")


async def create_upload(file: UploadFile, db: AsyncSession) -> dict:
    """Handle file upload: validate, save file, persist DB, cache, enqueue."""
    content_type = file.content_type or "application/octet-stream"
    file_id = str(uuid.uuid4())
    filename = os.path.basename(file.filename or "unnamed")
    _, ext = os.path.splitext(filename)
    dest_filename = f"{file_id}{ext}"

    # Get file size in memory (read temporarily to validate)
    contents = await file.read()
    size = len(contents)  # bytes
    size_mb = round(size / (1024 * 1024), 2)

    # Validate file size before saving
    if size_mb > settings.MAX_FILE_SIZE:
        logger.warning(
            "File upload rejected due to size limit: %s MB > %s MB",
            size_mb,
            settings.MAX_FILE_SIZE,
        )
        raise HTTPException(
            status_code=400,
            detail=(
                f"File size cannot exceed {settings.MAX_FILE_SIZE} MB. "
                f"Current file size is {size_mb} MB."
            ),
        )

    # Reset file pointer for saving
    await file.seek(0)

    # Ensure UPLOAD_DIR exists
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)

    dest_path = os.path.join(upload_dir, dest_filename)
    logger.info(f"Uploading file {filename} to {dest_path}")

    # Save file to disk
    await save_file_to_disk(file, dest_path)

    # Persist metadata
    try:
        meta = await save_upload_metadata(file_id, filename, content_type, size, dest_path, db)
        print(f"meta : {meta}")
    except Exception:
        if os.path.exists(dest_path):
            os.remove(dest_path)
            logger.info(f"Removed orphaned file {dest_path}")
        raise

    # Cache metadata & enqueue job
    await cache_upload_metadata(file_id, meta)
    await enqueue_upload_job(file_id, meta)

    # Add derived property for MB
    meta["size_mb"] = size_mb
    return meta


async def get_upload(file_id: str, db: AsyncSession) -> dict:
    """Retrieve upload metadata from DB (UUID converted to str)."""
    result = await db.execute(select(Upload).where(Upload.id == file_id))
    upload: Optional[Upload] = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    size = getattr(upload, "size", 0)

    return {
        "id": str(upload.id),
        "filename": upload.filename,
        "content_type": upload.content_type,
        "size": size,
        "size_mb": round(size / (1024 * 1024), 2),
        "path": upload.path,
        "created_at": upload.created_at,
        "updated_at": upload.updated_at,
    }
