import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class TraceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate trace_id and correlation_id for each request
    and attach to request.state.
    """

    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.trace_id = trace_id
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Correlation-ID"] = correlation_id
        return response
