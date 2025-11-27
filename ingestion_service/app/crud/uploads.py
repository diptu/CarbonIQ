import asyncio
import logging
import uuid
from pathlib import Path
from typing import Any, Optional

import aiofiles
import aiofiles.os
from fastapi import HTTPException, UploadFile, status
from ingestion_service.app.core.config import settings
from ingestion_service.app.models.upload import Upload
from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Redis keys / queue names
UPLOAD_META_PREFIX = "upload:meta:"
UPLOAD_QUEUE_NAME = "ingest:queue"


# -------------------------------
# Helper Functions
# -------------------------------


async def safe_delete(path: Path):
    """Safely delete a file asynchronously, log failures."""
    try:
        await aiofiles.os.remove(path)
        logger.debug(f"Deleted file: {path}")
    except FileNotFoundError:
        logger.info(f"File already deleted: {path}")
    except OSError as e:
        logger.warning(f"Failed to delete file {path}: {e}")


async def save_file_to_disk(file: UploadFile, dest_path: Path, max_size_mb: float) -> int:
    """Save UploadFile to disk asynchronously in chunks with max size validation."""
    try:
        size = 0
        max_bytes = max_size_mb * 1024 * 1024

        async with aiofiles.open(dest_path, "wb") as out_file:
            while chunk := await file.read(1024 * 64):  # 64 KB
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File exceeds max size of {max_size_mb} MB",
                    )
                await out_file.write(chunk)

        await file.close()
        logger.debug(f"File saved to {dest_path} ({size} bytes)")
        return size
    except HTTPException:
        raise
    except OSError as e:
        logger.exception(f"File system error while saving file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File storage failed",
        )


async def save_upload_metadata(
    file_id: str,
    filename: str,
    content_type: str,
    size: int,
    path: Path,
    db: AsyncSession,
) -> dict:
    """Persist upload metadata to the database asynchronously."""
    try:
        async with db.begin():
            stmt = insert(Upload).values(
                id=file_id,
                filename=filename,
                content_type=content_type,
                size=size,
                path=str(path),
            )
            await db.execute(stmt)

        logger.debug(f"Upload metadata saved: {file_id}")
        return {
            "id": file_id,
            "filename": filename,
            "content_type": content_type,
            "size": size,
            "path": str(path),
        }
    except SQLAlchemyError as e:
        logger.exception(f"Failed to persist upload metadata: {e}")
        raise


async def cache_upload_metadata(
    redis_client: Optional[Any], file_id: str, meta: dict, expire_seconds: int = 3600
):
    """Cache upload metadata in Redis (best-effort)."""
    if not redis_client:
        return

    try:
        # Determine if the client method is async
        method = getattr(redis_client, "set", None)
        if method:
            result = method(f"{UPLOAD_META_PREFIX}{file_id}", str(meta), ex=expire_seconds)
            if asyncio.iscoroutine(result):
                await result
        logger.debug(f"Cached metadata for {file_id} in Redis")
    except Exception as e:
        logger.warning(f"Failed to cache metadata in Redis: {e}")


async def enqueue_upload_job(redis_client: Optional[Any], file_id: str, meta: dict):
    """Push a job to Redis queue for downstream processing (best-effort)."""
    if not redis_client:
        return

    try:
        method = getattr(redis_client, "rpush", None)
        if method:
            result = method(UPLOAD_QUEUE_NAME, str({"file_id": file_id, "meta": meta}))
            if asyncio.iscoroutine(result):
                await result
        logger.debug(f"Enqueued job for {file_id} in Redis queue")
    except Exception as e:
        logger.warning(f"Failed to enqueue background job: {e}")


# -------------------------------
# Main CRUD Functions
# -------------------------------


async def create_upload(
    file: UploadFile, db: AsyncSession, redis_client: Optional[Any] = None
) -> dict:
    """Handle file upload fully asynchronously."""
    content_type = file.content_type or "application/octet-stream"
    file_id = str(uuid.uuid4())
    filename = file.filename or "unnamed"
    ext = Path(filename).suffix
    dest_filename = f"{file_id}{ext}"

    # Prepare paths
    upload_dir = await asyncio.to_thread(lambda: Path(settings.UPLOAD_DIR).resolve())
    dest_path = upload_dir / dest_filename
    await asyncio.to_thread(upload_dir.mkdir, parents=True, exist_ok=True)

    logger.info(f"Uploading file {filename} to {dest_path}")

    # Save file asynchronously
    try:
        size = await save_file_to_disk(file, dest_path, settings.MAX_FILE_SIZE)
    except HTTPException:
        await safe_delete(dest_path)
        raise

    size_mb = round(size / (1024 * 1024), 2)

    # Persist metadata
    try:
        meta = await save_upload_metadata(file_id, filename, content_type, size, dest_path, db)
    except Exception:
        await safe_delete(dest_path)
        raise

    # Fire-and-forget caching and enqueue
    if redis_client:
        asyncio.create_task(cache_upload_metadata(redis_client, file_id, meta))
        asyncio.create_task(enqueue_upload_job(redis_client, file_id, meta))

    meta["size_mb"] = size_mb
    return meta


async def get_upload(file_id: str, db: AsyncSession) -> dict:
    """Retrieve upload metadata from DB asynchronously."""
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
        "path": str(upload.path) if upload.path else None,
        "created_at": upload.created_at,
        "updated_at": upload.updated_at,
    }
