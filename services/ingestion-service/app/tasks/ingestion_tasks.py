"""Background pipeline: validate an uploaded file, then dispatch it downstream.

Both tasks are sync (Celery's native mode) but call into the service's
async DB/storage layer via `asyncio.run`, since each prefork worker process
handles one task at a time and can safely own a short-lived event loop.

Each `asyncio.run()` call creates and tears down its own event loop, but
`engine`/`AsyncSessionLocal` (app/db.py) are created once at import time and
shared by every task invocation. asyncpg's pooled connections are bound to
the loop that opened them, so reusing the pool from a *new* loop breaks
(harmlessly on Linux, but hard-crashes with an `AttributeError` on Windows'
ProactorEventLoop). Disposing the pool at the end of every task forces a
fresh connection on the next invocation's loop instead of reusing a stale
one — see https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-multiple-asyncio-event-loops.
"""

import asyncio
import logging
import uuid
from collections.abc import Coroutine
from typing import Any

import httpx

from app.celery_app import celery_app
from app.config import get_settings
from app.db import AsyncSessionLocal, engine
from app.models.ingested_file import IngestedFile, IngestionStatus
from app.storage.s3 import get_object_storage
from app.validators.base import validate_file

logger = logging.getLogger("ingestion_service.tasks")

# Which downstream service consumes each file type once it's validated.
_DISPATCH_TARGET_BY_FILE_TYPE = {
    "bill_pdf": "ocr-service",
    "bill_image": "ocr-service",
    "nem12_csv": "energy-data-service",
    "rec_certificate": "offset-service",
    "lgc_certificate": "offset-service",
    "ppa_contract": "offset-service",
}


async def _validate_file_async(file_id: uuid.UUID) -> IngestionStatus:
    storage = get_object_storage()

    async with AsyncSessionLocal() as session:
        record = await session.get(IngestedFile, file_id)
        if record is None:
            logger.warning("validate_file: no such ingested_file %s", file_id)
            return IngestionStatus.VALIDATION_FAILED

        record.status = IngestionStatus.VALIDATING
        await session.commit()

        content = storage.get_object_bytes(record.storage_key)
        result = validate_file(
            file_type=record.file_type,
            filename=record.original_filename,
            content_type=record.content_type,
            content=content,
        )

        record.status = (
            IngestionStatus.VALIDATED if result.is_valid else IngestionStatus.VALIDATION_FAILED
        )
        record.validation_errors = result.errors or None
        await session.commit()
        return record.status


async def _dispatch_file_async(file_id: uuid.UUID) -> IngestionStatus:
    settings = get_settings()

    async with AsyncSessionLocal() as session:
        record = await session.get(IngestedFile, file_id)
        if record is None:
            logger.warning("dispatch_file: no such ingested_file %s", file_id)
            return IngestionStatus.DISPATCH_FAILED

        if record.status != IngestionStatus.VALIDATED:
            logger.info(
                "dispatch_file: %s is not in VALIDATED state (got %s), skipping",
                file_id,
                record.status,
            )
            return record.status

        target = _DISPATCH_TARGET_BY_FILE_TYPE[record.file_type.value]
        record.status = IngestionStatus.DISPATCHING
        await session.commit()

        try:
            async with httpx.AsyncClient(timeout=settings.dispatch_timeout_seconds) as client:
                response = await client.post(
                    f"{settings.ocr_service_url}/api/v1/intake",
                    json={
                        "file_id": str(record.id),
                        "tenant_id": str(record.tenant_id),
                        "file_type": record.file_type.value,
                        "storage_bucket": record.storage_bucket,
                        "storage_key": record.storage_key,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            # Expected until the downstream service exists — logged, not raised,
            # so the record still reflects a clear terminal state for the API.
            logger.warning("dispatch_file: dispatch to %s failed: %s", target, exc)
            record.status = IngestionStatus.DISPATCH_FAILED
            await session.commit()
            return record.status

        record.status = IngestionStatus.DISPATCHED
        record.dispatched_to = target
        await session.commit()
        return record.status


async def _run_and_dispose(coro: Coroutine[Any, Any, IngestionStatus]) -> IngestionStatus:
    """Run `coro` to completion, then dispose the shared engine's connection
    pool before this event loop closes (see the module docstring)."""
    try:
        return await coro
    finally:
        await engine.dispose()


@celery_app.task(name="app.tasks.ingestion_tasks.validate_file_task", bind=True, max_retries=3)
def validate_file_task(self, file_id: str) -> str:
    status = asyncio.run(_run_and_dispose(_validate_file_async(uuid.UUID(file_id))))
    if status == IngestionStatus.VALIDATED:
        dispatch_file_task.delay(file_id)
    return status.value


@celery_app.task(
    name="app.tasks.ingestion_tasks.dispatch_file_task",
    bind=True,
    max_retries=5,
    default_retry_delay=30,
)
def dispatch_file_task(self, file_id: str) -> str:
    status = asyncio.run(_run_and_dispose(_dispatch_file_async(uuid.UUID(file_id))))
    if status == IngestionStatus.DISPATCH_FAILED:
        raise self.retry()
    return status.value
