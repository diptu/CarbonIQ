# app/tests/auth_test.py

import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ---------------------
# Constants
# ---------------------
TEST_USER = {
    "id": str(uuid.uuid4()),
    "roles": ["TENANT_ADMIN"],
    "permissions": ["user.read", "user.create", "billing.manage"],
    "tenant_id": None,
}

ACCESS_TOKEN = "access.token.mock"
REFRESH_TOKEN = "refresh.token.mock"


# ---------------------
# Mock helpers
# ---------------------
def mock_create_access_token(*args, **kwargs):
    payload = {
        "sub": TEST_USER["id"],
        "exp": int((datetime.utcnow() + timedelta(seconds=3600)).timestamp()),
        "jti": str(uuid.uuid4()),
        "roles": TEST_USER["roles"],
        "permissions": TEST_USER["permissions"],
        "tenant_id": TEST_USER["tenant_id"],
    }
    return ACCESS_TOKEN, payload


def mock_create_refresh_token(*args, **kwargs):
    payload = {
        "sub": TEST_USER["id"],
        "exp": int((datetime.utcnow() + timedelta(days=7)).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    return REFRESH_TOKEN, payload


def mock_decode_token(token):
    if token == REFRESH_TOKEN:
        return {
            "sub": TEST_USER["id"],
            "exp": int((datetime.utcnow() + timedelta(days=7)).timestamp()),
            "roles": TEST_USER["roles"],
            "permissions": TEST_USER["permissions"],
            "tenant_id": TEST_USER["tenant_id"],
            "jti": str(uuid.uuid4()),
        }
    raise Exception("Invalid token")


# ---------------------
# Fixtures
# ---------------------
@pytest.fixture
def mock_user_service():
    with patch("app.api.v1.routes.auth.requests.post", autospec=True) as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"data": TEST_USER}
        yield mock_post


@pytest.fixture
def mock_jwt_utils():
    with (
        patch("app.api.v1.routes.auth.create_access_token", side_effect=mock_create_access_token),
        patch("app.api.v1.routes.auth.create_refresh_token", side_effect=mock_create_refresh_token),
        patch("app.api.v1.routes.auth.decode_token", side_effect=mock_decode_token),
    ):
        yield


# ---------------------
# LOGIN TESTS
# ---------------------
@pytest.mark.usefixtures("mock_user_service", "mock_jwt_utils")
def test_login_success():
    payload = {"email": "test@example.com", "password": "secret"}
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["user_id"] == TEST_USER["id"]
    assert data["data"]["access_token"] == ACCESS_TOKEN
    assert data["data"]["refresh_token"] == REFRESH_TOKEN
    assert "access_expires_in" in data["data"]
    assert "refresh_expires_in" in data["data"]


def test_login_failure_invalid_credentials():
    with patch("app.api.v1.routes.auth.requests.post", autospec=True) as mock_post:
        mock_post.return_value.status_code = 401
        payload = {"email": "wrong@example.com", "password": "bad"}
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"


# ---------------------
# REFRESH TOKEN TESTS
# ---------------------
@pytest.mark.usefixtures("mock_jwt_utils")
def test_refresh_token_success():
    payload = {"refresh_token": REFRESH_TOKEN}
    response = client.post("/auth/refresh", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["data"]["access_token"] == ACCESS_TOKEN
    assert data["data"]["refresh_token"] == REFRESH_TOKEN


def test_refresh_token_failure_invalid():
    payload = {"refresh_token": "invalid.token"}
    response = client.post("/auth/refresh", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


# ---------------------
# LOGOUT TESTS
# ---------------------
@pytest.mark.usefixtures("mock_jwt_utils")
def test_logout_success():
    payload = {"refresh_token": REFRESH_TOKEN}
    response = client.post("/auth/logout", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["data"]["detail"] == "Successfully logged out"


def test_logout_failure_invalid_token():
    payload = {"refresh_token": "invalid.token"}
    response = client.post("/auth/logout", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
