import pytest
import uuid
from httpx import AsyncClient

# Base endpoint configuration
API_PREFIX = "/api/v1"
USERS_ENDPOINT = f"{API_PREFIX}/users"


@pytest.mark.asyncio
async def test_create_user(async_client: AsyncClient):
    payload = {
        "email": f"alice-{uuid.uuid4().hex[:6]}@example.com",
        "password": "wonderland",
    }

    response = await async_client.post(f"{USERS_ENDPOINT}/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_list_users(async_client: AsyncClient):
    payload = {
        "email": f"bob-{uuid.uuid4().hex[:6]}@example.com",
        "password": "builder",
    }
    create_resp = await async_client.post(f"{USERS_ENDPOINT}/", json=payload)
    assert create_resp.status_code == 201

    list_resp = await async_client.get(f"{USERS_ENDPOINT}/")
    assert list_resp.status_code == 200
    users = list_resp.json()

    assert isinstance(users, list)
    assert any(u["email"] == payload["email"] for u in users)


@pytest.mark.asyncio
async def test_get_user(async_client: AsyncClient):
    payload = {
        "email": f"charlie-{uuid.uuid4().hex[:6]}@example.com",
        "password": "chocolate",
    }
    create_resp = await async_client.post(f"{USERS_ENDPOINT}/", json=payload)
    assert create_resp.status_code == 201
    user = create_resp.json()

    resp = await async_client.get(f"{USERS_ENDPOINT}/{user['id']}")
    assert resp.status_code == 200
    fetched = resp.json()
    assert fetched["email"] == payload["email"]


@pytest.mark.asyncio
async def test_deactivate_user(async_client: AsyncClient):
    payload = {
        "email": f"deact-{uuid.uuid4().hex[:6]}@example.com",
        "password": "secret",
    }
    create_resp = await async_client.post(f"{USERS_ENDPOINT}/", json=payload)
    assert create_resp.status_code == 201
    user = create_resp.json()

    deactivate_resp = await async_client.patch(
        f"{USERS_ENDPOINT}/{user['id']}/deactivate"
    )
    assert deactivate_resp.status_code == 200
    deactivated = deactivate_resp.json()
    assert deactivated["is_active"] is False


@pytest.mark.asyncio
async def test_reactivate_user(async_client: AsyncClient):
    payload = {
        "email": f"react-{uuid.uuid4().hex[:6]}@example.com",
        "password": "secret",
    }
    create_resp = await async_client.post(f"{USERS_ENDPOINT}/", json=payload)
    assert create_resp.status_code == 201
    user = create_resp.json()

    await async_client.patch(f"{USERS_ENDPOINT}/{user['id']}/deactivate")

    reactivate_resp = await async_client.patch(
        f"{USERS_ENDPOINT}/{user['id']}/reactivate"
    )
    assert reactivate_resp.status_code == 200
    reactivated = reactivate_resp.json()
    assert reactivated["is_active"] is True


# -----------------------
# Negative test cases
# -----------------------


@pytest.mark.asyncio
async def test_deactivate_nonexistent_user(async_client: AsyncClient):
    resp = await async_client.patch(f"{USERS_ENDPOINT}/999999/deactivate")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_reactivate_nonexistent_user(async_client: AsyncClient):
    resp = await async_client.patch(f"{USERS_ENDPOINT}/999999/reactivate")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "User not found"
