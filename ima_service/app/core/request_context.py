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
    trace_id = f"req_{uuid4().hex}"
    correlation_id = f"corr_{uuid4().hex}"
    current_trace_id.set(trace_id)
    current_correlation_id.set(correlation_id)

    current_user_id.set(getattr(request.state, "user_id", None))
    current_email.set(getattr(request.state, "email", None))
    current_roles.set(getattr(request.state, "roles", []))
    current_permissions.set(getattr(request.state, "permissions", []))
    current_tenant_id.set(getattr(request.state, "tenant_id", None))
