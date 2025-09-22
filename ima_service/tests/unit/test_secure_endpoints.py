# ruff: noqa: D103
from __future__ import annotations
from fastapi.testclient import TestClient
from app.core.security import create_access_token
from app.core.settings import get_settings
from main import app

client = TestClient(app)
API = "/api/v1/secure"


def _auth(t: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {t}"}


def test_ping_requires_auth():
    r = client.get(f"{API}/ping")
    assert r.status_code == 401


def test_ping_ok_no_tenant():
    tok = create_access_token({"sub": "u1", "role": "viewer"})
    r = client.get(f"{API}/ping", headers=_auth(tok))
    assert r.status_code == 200
    assert r.json()["sub"] == "u1"
    assert r.json()["role"] == "viewer"
    assert r.json()["tenant"] is None


def test_ping_tenant_header_required_when_claim_present():
    tok = create_access_token({"sub": "u1", "role": "viewer", "tenant": "acme"})
    r = client.get(f"{API}/ping", headers=_auth(tok))  # missing header
    assert r.status_code == 400
    assert r.json()["code"] == "TENANT_HEADER_REQUIRED"


def test_ping_tenant_mismatch():
    tok = create_access_token({"sub": "u1", "role": "viewer", "tenant": "acme"})
    r = client.get(f"{API}/ping", headers={**_auth(tok), "X-Tenant-ID": "other"})
    assert r.status_code == 403
    assert r.json()["code"] == "TENANT_MISMATCH"


def test_owner_only_forbidden_for_viewer():
    tok = create_access_token({"sub": "u1", "role": "viewer"})
    r = client.get(f"{API}/owner", headers=_auth(tok))
    assert r.status_code == 403
    assert r.json()["code"] == "FORBIDDEN"


def test_owner_only_ok():
    tok = create_access_token({"sub": "u1", "role": "owner"})
    r = client.get(f"{API}/owner", headers=_auth(tok))
    assert r.status_code == 200
    assert r.json()["role"] == "owner"
