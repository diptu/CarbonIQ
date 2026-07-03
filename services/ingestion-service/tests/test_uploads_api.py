"""API-level tests for /api/v1/uploads, covering auth, validation, and
tenant isolation. The background validate/dispatch pipeline itself is
covered separately in test_ingestion_tasks.py — here we stub out the
Celery `.delay()` call so tests don't need a running broker.
"""

import uuid

import pytest
from httpx import AsyncClient

from app.core.security import AuthContext, get_current_auth
from app.main import app

PDF_BYTES = b"%PDF-1.4\nmock pdf content"


@pytest.fixture(autouse=True)
def _stub_celery_dispatch(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("app.api.v1.uploads.validate_file_task.delay", lambda *a, **k: None)


async def _upload(
    client: AsyncClient, filename="bill.pdf", file_type="bill_pdf", content=PDF_BYTES
):
    return await client.post(
        "/api/v1/uploads",
        files={"file": (filename, content, "application/pdf")},
        data={"file_type": file_type},
    )


async def test_create_upload_returns_pending_record(client: AsyncClient):
    response = await _upload(client)
    assert response.status_code == 201

    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "pending"
    assert body["data"]["original_filename"] == "bill.pdf"
    assert body["data"]["size_bytes"] == len(PDF_BYTES)
    assert "request_id" in body["meta"]


async def test_create_upload_rejects_empty_file(client: AsyncClient):
    response = await client.post(
        "/api/v1/uploads",
        files={"file": ("bill.pdf", b"", "application/pdf")},
        data={"file_type": "bill_pdf"},
    )
    assert response.status_code == 422
    assert response.json()["success"] is False


async def test_create_upload_rejects_oversized_file(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    from app import config

    monkeypatch.setenv("MAX_UPLOAD_SIZE_BYTES", "10")
    config.get_settings.cache_clear()
    try:
        response = await _upload(client, content=b"x" * 100)
        assert response.status_code == 413
    finally:
        config.get_settings.cache_clear()


async def test_create_upload_rejects_invalid_file_type(client: AsyncClient):
    response = await _upload(client, file_type="not_a_real_type")
    assert response.status_code == 422


async def test_list_uploads_returns_only_current_tenant(
    client: AsyncClient, auth_context: AuthContext
):
    await _upload(client)
    await _upload(client, filename="bill2.pdf")

    response = await client.get("/api/v1/uploads")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["total"] == 2
    assert len(body["items"]) == 2


async def test_get_upload_by_id(client: AsyncClient):
    created = (await _upload(client)).json()["data"]

    response = await client.get(f"/api/v1/uploads/{created['id']}")
    assert response.status_code == 200
    assert response.json()["data"]["id"] == created["id"]


async def test_get_upload_returns_404_for_unknown_id(client: AsyncClient):
    response = await client.get(f"/api/v1/uploads/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_get_upload_is_isolated_by_tenant(client: AsyncClient):
    created = (await _upload(client)).json()["data"]

    other_tenant_auth = AuthContext(
        user_id=str(uuid.uuid4()), tenant_id=str(uuid.uuid4()), roles=[], permissions=[]
    )
    app.dependency_overrides[get_current_auth] = lambda: other_tenant_auth
    response = await client.get(f"/api/v1/uploads/{created['id']}")

    assert response.status_code == 404


async def test_download_url_returns_presigned_link(client: AsyncClient):
    created = (await _upload(client)).json()["data"]

    response = await client.get(f"/api/v1/uploads/{created['id']}/download-url")
    assert response.status_code == 200
    assert response.json()["data"]["url"].startswith("https://fake-storage.local/")


async def test_delete_upload_removes_record(client: AsyncClient):
    created = (await _upload(client)).json()["data"]

    delete_response = await client.delete(f"/api/v1/uploads/{created['id']}")
    assert delete_response.status_code == 200

    get_response = await client.get(f"/api/v1/uploads/{created['id']}")
    assert get_response.status_code == 404


async def test_uploads_require_authentication():
    from httpx import ASGITransport

    app.dependency_overrides.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as unauth_client:
        response = await unauth_client.get("/api/v1/uploads")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "unauthorized"
