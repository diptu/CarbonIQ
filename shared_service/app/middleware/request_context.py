import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate IDs if not present
        request.state.trace_id = str(uuid.uuid4())
        request.state.correlation_id = request.headers.get(
            "X-Correlation-ID", str(uuid.uuid4())
        )

        # Optional auth context (depends on JWT or session setup)
        request.state.user_id = request.headers.get("X-User-ID")
        request.state.tenant_id = request.headers.get("X-Tenant-ID")

        # Roles & permissions could be parsed from JWT in real flow
        request.state.roles = []
        request.state.permissions = []

        response = await call_next(request)

        # Add IDs to response headers for tracing
        response.headers["X-Trace-ID"] = request.state.trace_id
        response.headers["X-Correlation-ID"] = request.state.correlation_id

        return response
