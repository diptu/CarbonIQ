"""Minimal tests for server and database health routes."""

from __future__ import annotations

import importlib

import pytest
from httpx import ASGITransport, AsyncClient
from ima_service.app.main import app


@pytest.mark.asyncio
async def test_server_health_endpoint_ok() -> None:
    """Server health endpoint should return 200 and ok payload."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/server")

    body = resp.json()
    assert resp.status_code == 200
    assert body["code"] == 200
    assert body["status"] == "success"
    assert body["data"]["status"] == "ok"
    assert body["data"]["details"]["server"] == "ok"


@pytest.mark.asyncio
async def test_database_health_missing_config_returns_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Database route returns fail when settings are missing/invalid."""
    # Ensure modules are imported (router defines the route, service holds logic)
    import importlib
    import ima_service.app.api.v1.health.router  # noqa: F401

    # Patch where get_settings() is actually used now
    svc_db_mod = importlib.import_module(
        "ima_service.app.api.v1.health.services.database"
    )

    def _raise():
        raise RuntimeError("no env")

    monkeypatch.setattr(svc_db_mod, "get_settings", _raise, raising=True)

    from httpx import ASGITransport, AsyncClient
    from ima_service.app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health/database")

    body = resp.json()
    # HTTP stays 200; envelope carries the failure code/status.
    assert resp.status_code == 200
    assert body["code"] == 503
    assert body["status"] == "error"
    assert body["data"]["status"] == "fail"
    assert body["data"]["details"]["database"] == "fail"
