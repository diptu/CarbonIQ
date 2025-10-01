import pytest
import uuid
from httpx import AsyncClient
from ima_service.app.main import app


@pytest.mark.asyncio
async def test_user_crud_and_auth_flow(async_client: AsyncClient):
    # -------------------------
    # Generate a random email
    # -------------------------
    rand_uid = str(uuid.uuid4())[:8]
    test_email = f"user_{rand_uid}@example.com"

    # Example payload
    payload = {
        "email": test_email,
        "isActive": True,
        "isSuperuser": False,
        "password": "TestPass123!",
        "full_name": "Test User",
    }

    # -------------------------
    # 1️⃣ Create user
    # -------------------------
    create_resp = await async_client.post("/api/v1/users/", json=payload)
    assert create_resp.status_code == 201
    user_data = create_resp.json().get("details", {})
    user_id = user_data["id"]
    assert user_data["email"] == payload["email"]

    # -------------------------
    # 2️⃣ Get user by ID
    # -------------------------
    get_resp = await async_client.get(f"/api/v1/users/{user_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json().get("details", {})
    assert get_data["email"] == payload["email"]

    # -------------------------
    # 3️⃣ Update user
    # -------------------------
    updated_payload = {"isActive": False, "isSuperuser": True}
    update_resp = await async_client.put(
        f"/api/v1/users/{user_id}", json=updated_payload
    )
    assert update_resp.status_code == 200
    updated_data = update_resp.json().get("details", {})
    assert updated_data["isActive"] is False
    assert updated_data["isSuperuser"] is True

    # -------------------------
    # 4️⃣ List users
    # -------------------------
    list_resp = await async_client.get("/api/v1/users/?skip=0&limit=100")
    assert list_resp.status_code == 200
    users_items = list_resp.json().get("details", {}).get("items", [])
    emails = [u["email"] for u in users_items]
    assert payload["email"] in emails

    # -------------------------
    # 5️⃣ Deactivate user
    # -------------------------
    deactivate_resp = await async_client.post(f"/api/v1/users/{user_id}/deactivate")
    assert deactivate_resp.status_code == 200
    deactivate_data = deactivate_resp.json().get("details", {})
    assert deactivate_data["isActive"] is False

    # -------------------------
    # 6️⃣ Reactivate user
    # -------------------------
    reactivate_resp = await async_client.post(f"/api/v1/users/{user_id}/reactivate")
    assert reactivate_resp.status_code == 200
    reactivate_data = reactivate_resp.json().get("details", {})
    assert reactivate_data["isActive"] is True

    # -------------------------
    # 7️⃣ Authentication flow
    # -------------------------
    login_payload = {"email": test_email, "password": payload["password"]}
    login_resp = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200

    tokens = login_resp.json().get("details", {})
    access_token = tokens["accessToken"]
    refresh_token = tokens["refreshToken"]
    token_type = tokens["tokenType"]
    expires_in = tokens["expiresIn"]

    assert token_type.lower() == "bearer"
    assert access_token and refresh_token and expires_in > 0

    # Refresh token
    refresh_resp = await async_client.post(
        "/api/v1/auth/refresh", json={"refreshToken": refresh_token}
    )
    assert refresh_resp.status_code == 200
    new_access_token = refresh_resp.json().get("accessToken", {})
    new_refresh_token = refresh_resp.json().get("refreshToken", {})

    assert new_access_token != ""
    assert new_refresh_token != ""

    # Logout
    logout_resp = await async_client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {new_access_token}"},
    )
    assert logout_resp.status_code == 200

    # Attempt login with wrong password
    wrong_login = await async_client.post(
        "/api/v1/auth/login", json={"email": test_email, "password": "wrongpass"}
    )
    assert wrong_login.status_code == 401

    # -------------------------
    # 8️⃣ Delete user
    # -------------------------
    delete_resp = await async_client.delete(f"/api/v1/users/{user_id}")
    assert delete_resp.status_code == 204

    # Confirm deletion
    get_deleted_resp = await async_client.get(f"/api/v1/users/{user_id}")
    assert get_deleted_resp.status_code == 404
