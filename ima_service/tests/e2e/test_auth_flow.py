# ima_service/tests/e2e/test_auth_flow.py
"""E2E auth flow: login → refresh (rotation) → logout (+ RBAC/tenant checks)."""

from __future__ import annotations

from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient

# App entrypoint
from ima_service.main import app  # type: ignore

# Modules we patch
import ima_service.app.api.v1.auth as auth_mod  # type: ignore
import ima_service.app.core.settings as settings_mod  # type: ignore
from ima_service.app.core.token_store import get_token_store  # type: ignore


# ---------------------------
# Test helpers & fakes
# ---------------------------
class _Secret:
    def __init__(self, v: str) -> None:
        self._v = v

    def get_secret_value(self) -> str:
        return self._v


class _JwtCfg:
    algorithm: str = "HS256"
    access_expire_minutes: int = 5
    refresh_expire_days: int = 1
    secret_key: _Secret = _Secret("test-secret")


class _TestSettings:
    """Minimal settings stub exposing only attributes used by security/auth."""

    def __init__(self) -> None:
        self.jwt = _JwtCfg()


class _FakeUser:
    def __init__(self, user_id: str, role: str) -> None:
        self.id = user_id
        self.role = role


class _FakeTokenStore:
    """In-memory refresh-token store with the same interface as TokenStore."""

    def __init__(self) -> None:
        self._active: Dict[str, str] = {}  # jti -> user_id
        self._by_user: Dict[str, set[str]] = {}
        self._blocked: set[str] = set()

    # --- lifecycle ----
    async def mark_refresh_active(self, *, user_id: str, jti: str, ttl_s: int) -> None:
        self._active[jti] = user_id
        self._by_user.setdefault(user_id, set()).add(jti)

    async def is_refresh_active(self, jti: str) -> bool:
        return jti in self._active

    async def revoke_refresh(self, jti: str, *, user_id: str | None = None) -> None:
        self._active.pop(jti, None)
        if user_id is not None:
            self._by_user.get(user_id, set()).discard(jti)

    async def rotate_refresh(
        self, *, user_id: str, old_jti: str, new_jti: str, ttl_s: int
    ) -> None:
        self._active.pop(old_jti, None)
        self._active[new_jti] = user_id
        s = self._by_user.setdefault(user_id, set())
        s.discard(old_jti)
        s.add(new_jti)

    async def revoke_all_for_user(self, user_id: str) -> int:
        jt_is = list(self._by_user.get(user_id, set()))
        for j in jt_is:
            self._active.pop(j, None)
        self._by_user.pop(user_id, None)
        return len(jt_is)

    # --- block switch ----
    async def block_user(self, user_id: str, ttl_s: int) -> None:
        self._blocked.add(user_id)

    async def unblock_user(self, user_id: str) -> None:
        self._blocked.discard(user_id)

    async def is_user_blocked(self, user_id: str) -> bool:
        return user_id in self._blocked

    # --- utils (not used) ----
    async def drop_keys(self, keys) -> int:  # pragma: no cover
        return 0


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    """
    Provide a TestClient with:
      - patched get_settings() → stable test secret,
      - fake token store (no Redis),
      - stub authenticate_user().
    """
    test_settings = _TestSettings()
    fake_store = _FakeTokenStore()

    # Patch global settings accessor used by security helpers.
    monkeypatch.setattr(settings_mod, "get_settings", lambda: test_settings)

    # Patch dependency for token store.
    async def _store_override() -> _FakeTokenStore:
        return fake_store

    app.dependency_overrides[get_token_store] = _store_override

    # Default: authenticate as admin unless overridden in a test.
    def _fake_auth(email: str, password: str) -> _FakeUser | None:  # noqa: ARG001
        role = "admin"
        if email.startswith("user@"):
            role = "user"
        return _FakeUser("u1", role)

    monkeypatch.setattr(auth_mod, "authenticate_user", _fake_auth)

    return TestClient(app)


# ---------------------------
# Tests
# ---------------------------
def _login(
    client: TestClient, email: str, password: str, tenant: Optional[str] = None
) -> dict[str, Any]:
    headers: Dict[str, str] = {}
    if tenant:
        headers["X-Tenant-ID"] = tenant
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_login_refresh_logout_flow(client: TestClient) -> None:
    # 1) Login (tenant-bound)
    j = _login(client, "admin@example.com", "secret", tenant="tenant_a")
    access1 = j["access_token"]
    refresh1 = j["refresh_token"]

    # Access a protected endpoint (admin + tenant match required)
    r = client.get(
        "/api/v1/secure/ping",
        headers={
            "Authorization": f"Bearer {access1}",
            "X-Tenant-ID": "tenant_a",
        },
    )
    assert r.status_code == 200, r.text
    assert r.json()["ok"] is True

    # 2) Refresh (rotation)
    r2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh1})
    assert r2.status_code == 200, r2.te_
