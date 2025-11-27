import logging
from pathlib import Path
from typing import Any, Optional

import aiofiles
from fastapi import HTTPException, UploadFile
from ingestion_service.app.core.config import settings
from ingestion_service.app.models.upload import Upload
from sqlalchemy import insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

UPLOAD_META_PREFIX = "upload:meta:"
UPLOAD_QUEUE_NAME = "ingest:queue"
CHUNK_SIZE = int(settings.CHUNK_SIZE) * 1024  # 64 KB


# -------------------------------
# Helpers
# -------------------------------


async def save_file(file: UploadFile, dest_path: Path) -> int:
    """Save UploadFile to disk asynchronously in chunks."""
    size = 0
    try:
        async with aiofiles.open(dest_path, "wb") as out_file:
            while chunk := await file.read(CHUNK_SIZE):
                size += len(chunk)
                await out_file.write(chunk)
        await file.close()
        logger.debug(f"File saved to {dest_path} ({size} bytes)")
        return size
    except Exception as e:
        logger.exception(f"Failed to save file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")


async def save_file_from_path(src_path: Path, dest_path: Path) -> int:
    """Save file from temp path to final destination asynchronously."""
    size = 0
    try:
        async with aiofiles.open(src_path, "rb") as in_file:
            async with aiofiles.open(dest_path, "wb") as out_file:
                while chunk := await in_file.read(CHUNK_SIZE):
                    size += len(chunk)
                    await out_file.write(chunk)
        return size
    except Exception as e:
        logger.exception(f"Failed to save file from path: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.")


async def save_upload_metadata(
    file_id: str, filename: str, content_type: str, size: int, path: Path, db: AsyncSession
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

        return {
            "id": str(file_id),
            "filename": filename,
            "content_type": content_type,
            "size": size,
            "size_mb": round(size / (1024 * 1024), 2),
            "path": str(path),
        }
    except SQLAlchemyError as e:
        logger.exception(f"Failed to persist upload metadata: {e}")
        raise HTTPException(status_code=500, detail="Failed to save metadata.")


async def cache_upload_metadata(
    redis_client: Any, file_id: str, meta: dict, expire_seconds: int = 3600
):
    """Cache upload metadata in Redis (best-effort)."""
    try:
        await redis_client.set(f"{UPLOAD_META_PREFIX}{file_id}", str(meta), ex=expire_seconds)
        logger.debug(f"Cached metadata for {file_id}")
    except Exception as e:
        logger.warning(f"Failed to cache metadata in Redis: {e}")


async def enqueue_upload_job(redis_client: Any, file_id: str, meta: dict):
    """Enqueue background job in Redis (best-effort)."""
    try:
        await redis_client.rpush(UPLOAD_QUEUE_NAME, str({"file_id": file_id, "meta": meta}))
        logger.debug(f"Enqueued job for {file_id}")
    except Exception as e:
        logger.warning(f"Failed to enqueue job: {e}")


async def get_upload(file_id: str, db: AsyncSession) -> dict:
    """Retrieve upload metadata from DB asynchronously."""
    result = await db.execute(select(Upload).where(Upload.id == file_id))
    upload: Optional[Upload] = result.scalar_one_or_none()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return {
        "id": str(upload.id),
        "filename": upload.filename,
        "content_type": upload.content_type,
        "size": upload.size,
        "size_mb": round(upload.size / (1024 * 1024), 2) if upload.size else None,
        "path": str(upload.path),
        "created_at": upload.created_at,
        "updated_at": upload.updated_at,
    }
