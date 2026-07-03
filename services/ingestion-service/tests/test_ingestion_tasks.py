"""Tests for the validate -> dispatch background pipeline.

These call the async helper coroutines directly (rather than going through
Celery's `.delay()`), with `app.tasks.ingestion_tasks.AsyncSessionLocal` and
the object store monkeypatched so no real Postgres/S3/broker is needed.
"""

import io
import uuid

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingested_file import FileType, IngestedFile, IngestionStatus
from app.tasks import ingestion_tasks

NEM12_BYTES = b"100,NEM12\n200,NMI0000001\n900\n"


@pytest.fixture
async def seeded_file(db_session: AsyncSession, fake_storage, tenant_id, user_id) -> IngestedFile:
    key = f"{tenant_id}/nem12_csv/{uuid.uuid4()}_interval.csv"
    fake_storage.put_object(key, io.BytesIO(NEM12_BYTES), "text/csv")

    record = IngestedFile(
        tenant_id=uuid.UUID(tenant_id),
        uploaded_by=uuid.UUID(user_id),
        file_type=FileType.NEM12_CSV,
        original_filename="interval.csv",
        content_type="text/csv",
        size_bytes=len(NEM12_BYTES),
        checksum_sha256="deadbeef",
        storage_bucket=fake_storage.bucket,
        storage_key=key,
        status=IngestionStatus.PENDING,
    )
    db_session.add(record)
    await db_session.commit()
    await db_session.refresh(record)
    return record


@pytest.fixture(autouse=True)
def _patch_task_session_and_storage(monkeypatch, db_session, fake_storage):
    from sqlalchemy.ext.asyncio import async_sessionmaker

    class _SingleSessionMaker:
        """Returns the same test session every time, mimicking a sessionmaker
        context manager without opening a new SQLite connection per call."""

        def __call__(self):
            return _NoCloseSessionCtx(db_session)

    class _NoCloseSessionCtx:
        def __init__(self, session):
            self._session = session

        async def __aenter__(self):
            return self._session

        async def __aexit__(self, *exc_info):
            return False

    monkeypatch.setattr(ingestion_tasks, "AsyncSessionLocal", _SingleSessionMaker())
    monkeypatch.setattr(ingestion_tasks, "get_object_storage", lambda: fake_storage)
    assert async_sessionmaker  # keep import referenced for clarity


async def test_validate_file_marks_valid_nem12_as_validated(seeded_file: IngestedFile):
    status = await ingestion_tasks._validate_file_async(seeded_file.id)
    assert status == IngestionStatus.VALIDATED


async def test_validate_file_marks_malformed_file_as_validation_failed(
    db_session: AsyncSession, fake_storage, tenant_id, user_id
):
    key = f"{tenant_id}/nem12_csv/bad.csv"
    fake_storage.put_object(key, io.BytesIO(b"not,a,valid,nem12,file"), "text/csv")

    record = IngestedFile(
        tenant_id=uuid.UUID(tenant_id),
        uploaded_by=uuid.UUID(user_id),
        file_type=FileType.NEM12_CSV,
        original_filename="bad.csv",
        content_type="text/csv",
        size_bytes=10,
        checksum_sha256="deadbeef",
        storage_bucket=fake_storage.bucket,
        storage_key=key,
        status=IngestionStatus.PENDING,
    )
    db_session.add(record)
    await db_session.commit()
    await db_session.refresh(record)

    status = await ingestion_tasks._validate_file_async(record.id)
    assert status == IngestionStatus.VALIDATION_FAILED
    await db_session.refresh(record)
    assert record.validation_errors


async def test_dispatch_file_marks_dispatched_on_success(
    seeded_file: IngestedFile, monkeypatch: pytest.MonkeyPatch, db_session: AsyncSession
):
    seeded_file.status = IngestionStatus.VALIDATED
    await db_session.commit()

    async def _mock_post(self, url, json=None, **kwargs):
        return httpx.Response(
            200, json={"accepted": True}, request=httpx.Request("POST", url)
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", _mock_post)

    status = await ingestion_tasks._dispatch_file_async(seeded_file.id)
    assert status == IngestionStatus.DISPATCHED
    await db_session.refresh(seeded_file)
    assert seeded_file.dispatched_to == "energy-data-service"


async def test_dispatch_file_marks_failed_when_downstream_unreachable(
    seeded_file: IngestedFile, monkeypatch: pytest.MonkeyPatch, db_session: AsyncSession
):
    seeded_file.status = IngestionStatus.VALIDATED
    await db_session.commit()

    async def _mock_post(self, url, json=None, **kwargs):
        raise httpx.ConnectError("connection refused", request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", _mock_post)

    status = await ingestion_tasks._dispatch_file_async(seeded_file.id)
    assert status == IngestionStatus.DISPATCH_FAILED


async def test_dispatch_file_skips_non_validated_records(seeded_file: IngestedFile):
    assert seeded_file.status == IngestionStatus.PENDING

    status = await ingestion_tasks._dispatch_file_async(seeded_file.id)
    assert status == IngestionStatus.PENDING
