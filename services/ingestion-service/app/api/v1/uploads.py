"""Upload intake API: POST to stage a file, GET to check status/list history.

Every route is tenant-scoped off the caller's JWT (`AuthContext.tenant_id`) —
a request can never see or touch another tenant's files.
"""

import hashlib
import io
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.config import Settings, get_settings
from app.core.responses import success_envelope
from app.core.security import AuthContext, get_current_auth
from app.db import get_db
from app.models.ingested_file import FileType, IngestedFile, IngestionStatus
from app.schemas.ingested_file import IngestedFilePage, IngestedFileRead
from app.storage.s3 import ObjectStorage, get_object_storage
from app.tasks.ingestion_tasks import validate_file_task

router = APIRouter(prefix="/uploads", tags=["uploads"])


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")


async def _get_owned_upload(
    upload_id: uuid.UUID, tenant_id: str, db: AsyncSession
) -> IngestedFile:
    record = await db.get(IngestedFile, upload_id)
    if record is None or str(record.tenant_id) != tenant_id:
        raise _not_found()
    return record


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_upload(
    file: UploadFile = File(...),
    file_type: FileType = Form(...),
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
    storage: ObjectStorage = Depends(get_object_storage),
    settings: Settings = Depends(get_settings),
) -> dict:
    content = await file.read()

    if not content:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, "Uploaded file is empty")
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE,
            f"File exceeds the {settings.max_upload_size_bytes} byte upload limit",
        )

    checksum = hashlib.sha256(content).hexdigest()
    storage_key = f"{auth.tenant_id}/{file_type.value}/{uuid.uuid4()}_{file.filename}"

    record = IngestedFile(
        tenant_id=uuid.UUID(auth.tenant_id),
        uploaded_by=uuid.UUID(auth.user_id),
        file_type=file_type,
        original_filename=file.filename or "unnamed",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(content),
        checksum_sha256=checksum,
        storage_bucket=storage.bucket,
        storage_key=storage_key,
        status=IngestionStatus.PENDING,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    await run_in_threadpool(
        storage.put_object, storage_key, io.BytesIO(content), record.content_type
    )

    validate_file_task.delay(str(record.id))

    return success_envelope(IngestedFileRead.model_validate(record).model_dump(mode="json"))


@router.get("")
async def list_uploads(
    page: int = 1,
    size: int = 20,
    file_type: FileType | None = None,
    upload_status: IngestionStatus | None = None,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
) -> dict:
    page = max(page, 1)
    size = min(max(size, 1), 100)

    filters = [IngestedFile.tenant_id == uuid.UUID(auth.tenant_id)]
    if file_type is not None:
        filters.append(IngestedFile.file_type == file_type)
    if upload_status is not None:
        filters.append(IngestedFile.status == upload_status)

    total = await db.scalar(
        select(func.count()).select_from(IngestedFile).where(*filters)
    )

    result = await db.execute(
        select(IngestedFile)
        .where(*filters)
        .order_by(IngestedFile.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = result.scalars().all()

    page_data = IngestedFilePage(
        items=[IngestedFileRead.model_validate(item) for item in items],
        page=page,
        size=size,
        total=total or 0,
    )
    return success_envelope(page_data.model_dump(mode="json"))


@router.get("/{upload_id}")
async def get_upload(
    upload_id: uuid.UUID,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
) -> dict:
    record = await _get_owned_upload(upload_id, auth.tenant_id, db)
    return success_envelope(IngestedFileRead.model_validate(record).model_dump(mode="json"))


@router.get("/{upload_id}/download-url")
async def get_download_url(
    upload_id: uuid.UUID,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
    storage: ObjectStorage = Depends(get_object_storage),
) -> dict:
    record = await _get_owned_upload(upload_id, auth.tenant_id, db)
    url = await run_in_threadpool(storage.presigned_get_url, record.storage_key)
    return success_envelope({"url": url, "expires_in": 900})


@router.delete("/{upload_id}", status_code=status.HTTP_200_OK)
async def delete_upload(
    upload_id: uuid.UUID,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
    storage: ObjectStorage = Depends(get_object_storage),
) -> dict:
    record = await _get_owned_upload(upload_id, auth.tenant_id, db)
    await run_in_threadpool(storage.delete_object, record.storage_key)
    await db.delete(record)
    await db.commit()
    return success_envelope(None)
