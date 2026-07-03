"""Health check is unauthenticated and reports DB reachability."""

from httpx import AsyncClient


async def test_healthz_ok_with_working_db(client: AsyncClient):
    response = await client.get("/api/v1/healthz")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["service"] == "ingestion-service"
