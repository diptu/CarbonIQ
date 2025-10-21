# app/core/middleware.py
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from uuid import uuid4
from app.core.audit_adapter import (
    current_trace_id,
    current_correlation_id,
)


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # generate trace & correlation ids per request
        current_trace_id.set(f"req_{uuid4().hex}")
        current_correlation_id.set(f"corr_{uuid4().hex}")

        response = await call_next(request)
        return response
