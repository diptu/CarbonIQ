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
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        resp = await client.get("/v1/health/server")

    body = resp.json()
    assert resp.status_code == 200
    assert body["code"] == 200
    assert body["status"] == "success"
    assert body["data"]["status"] == "ok"
    # details may be None in minimal payload


@pytest.mark.asyncio
async def test_database_health_missing_config_returns_fail(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Database health returns 503 when session manager cannot be created."""
    # Ensure route module is imported (registers the route)
    import ima_service.app.api.v1.health.router  # noqa: F401

    # Patch where it's used now: services.database.get_session_manager
    svc_db_mod = importlib.import_module(
        "ima_service.app.api.v1.health.services.database"
    )

    def _boom() -> None:
        raise RuntimeError("no env")

    monkeypatch.setattr(svc_db_mod, "get_session_manager", _boom, raising=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test"
    ) as client:
        resp = await client.get("/v1/health/database")

    body = resp.json()
    # HTTP status now matches payload code
    assert resp.status_code == 503
    assert body["code"] == 503
    assert body["status"] == "error"
    assert body["data"]["status"] == "fail"
    # details may be None in minimal payload
