# app/core/middleware/context.py
from typing import Optional
from fastapi import Request
from uuid import uuid4
from .audit_adapter import (
    current_user_id,
    current_email,
    current_roles,
    current_permissions,
    current_tenant_id,
    current_trace_id,
    current_correlation_id,
)


async def set_request_context(request: Request):
    # Automatically generate unique IDs
    current_trace_id.set(f"trace_{uuid4().hex}")
    current_correlation_id.set(f"corr_{uuid4().hex}")

    # Infer logged-in user data
    current_user_id.set(getattr(request.state, "user_id", None))
    current_email.set(getattr(request.state, "email", None))
    current_roles.set(getattr(request.state, "roles", []))
    current_permissions.set(getattr(request.state, "permissions", []))
    current_tenant_id.set(getattr(request.state, "tenant_id", None))
