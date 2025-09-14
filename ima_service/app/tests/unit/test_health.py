"""Minimal tests for health endpoints and docs helpers."""

from __future__ import annotations

import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from ima_service.app.api.v1.health.utils import HealthService
from ima_service.app.main import app


@pytest.mark.asyncio
async def test_server_health_endpoint_ok() -> None:
    """Endpoint should return 200 and ok."""
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        resp = await client.get("/health/server")

    body = resp.json()
    assert resp.status_code == 200
    assert body["status"] == "success"
    assert body["data"]["status"] == "ok"
    assert body["data"]["details"]["server"] == "ok"


@pytest.mark.asyncio
async def test_health_service_timeout() -> None:
    """Timeout path returns 500 with kind=timeout."""

    async def slow() -> bool:
        await asyncio.sleep(0.2)
        return True

    service = HealthService("Slow", slow, "slow", timeout_sec=0.05)
    resp = await service()

    assert resp.code == 500
    assert resp.status == "error"
    assert resp.details is not None
    assert resp.details["kind"] == "timeout"


def test_health_docs_all_and_unknown_drop() -> None:
    """Docs: grouped view + drop unknown keys branch."""
    from ima_service.app.api.v1.health.docs import HEALTH_DOCS, openapi_doc

    # grouped view covers cached properties
    grouped = HEALTH_DOCS.all
    assert set(grouped) == {"server", "database", "redis", "full"}

    # create a doc with an unknown key to hit drop branch
    class T:
        @openapi_doc(summary="s", description="d")
        def foo(self) -> dict[str, object]:
            return {"unknown_key": 123}

    kwargs = T().foo
    assert kwargs["summary"] == "s"
    assert kwargs["description"] == "d"
    assert "unknown_key" not in kwargs
    assert "openapi_extra" not in kwargs  # no extras produced


def test_openapi_doc_normalizes_operation_ids() -> None:
    """operationId and operation_id → openapi_extra.operationId."""
    from ima_service.app.api.v1.health.docs import openapi_doc

    class A:
        @openapi_doc(summary="s", description="d")
        def foo(self) -> dict[str, object]:
            return {"operationId": "camel", "tags": ["x"]}

    class B:
        @openapi_doc(summary="s", description="d")
        def bar(self) -> dict[str, object]:
            return {"operation_id": "snake", "tags": ["y"]}

    a = A().foo
    b = B().bar
    assert a["openapi_extra"]["operationId"] == "camel"
    assert b["openapi_extra"]["operationId"] == "snake"
    assert a["tags"] == ["x"] and b["tags"] == ["y"]


def test_openapi_doc_no_openapi_extra() -> None:
    """When no extras exist, openapi_extra is absent."""
    from ima_service.app.api.v1.health.docs import openapi_doc

    class T:
        @openapi_doc(summary="s", description="d")
        def foo(self) -> dict[str, object] | None:
            return None

    kwargs = T().foo
    assert kwargs["summary"] == "s"
    assert kwargs["description"] == "d"
    assert "openapi_extra" not in kwargs
