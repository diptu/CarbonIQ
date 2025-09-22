"""Custom OpenAPI (tags, servers, error schema, OAuth2)."""

from __future__ import annotations
from typing import Any, Dict, List
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from ..core.settings import Settings

_TAGS: List[Dict[str, Any]] = [
    {"name": "health", "description": "Service heartbeat & metadata."},
    {"name": "auth", "description": "JWT login/refresh/logout."},
    {"name": "users", "description": "User management (RBAC, tenant-aware)."},
]

_ERROR_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "code": {"type": "string", "example": "INVALID_CREDENTIALS"},
        "message": {"type": "string", "example": "Invalid credentials."},
        "details": {"type": "object", "additionalProperties": True},
    },
    "required": ["code", "message"],
}


def build_openapi(app: FastAPI, st: Settings) -> Dict[str, Any]:
    """Return OpenAPI dict customized for IMA."""
    schema = get_openapi(
        title=st.app_name,
        version="0.1.0",
        description=(
            "Authentication & RBAC service.\n\n"
            "- OAuth2 password flow → **/api/v1/auth/login**\n"
            "- Token rotation + reuse detection on **/refresh**\n"
            "- Tenant header: `X-Tenant-ID` must match token `tenant` claim\n"
            "- Roles: `owner`, `editor`, `viewer`"
        ),
        routes=app.routes,
    )
    schema.setdefault("tags", _TAGS)
    schema.setdefault("servers", [{"url": "/", "description": "Current host"}])
    comps = schema.setdefault("components", {})
    comps.setdefault("schemas", {})["Error"] = _ERROR_SCHEMA
    comps.setdefault("securitySchemes", {})["OAuth2PasswordBearer"] = {
        "type": "oauth2",
        "flows": {"password": {"tokenUrl": "/api/v1/auth/login", "scopes": {}}},
    }
    # Global 401/403 examples (kept minimal)
    schema.setdefault("components", comps)
    return schema
