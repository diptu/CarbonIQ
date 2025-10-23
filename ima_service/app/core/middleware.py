# app/core/middleware.py
"""
FastAPI / Starlette middleware for per-request context management.

Responsibilities:
- Initialize trace_id and correlation_id
- Populate user/tenant/roles/permissions from request.state
- Log unhandled exceptions via audit_logger
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from uuid import uuid4
from typing import Callable

from app.core.context import (
    set_request_context,
    init_trace_ids,
)
from app.core.audit_adapter import audit_logger


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware to populate ContextVars and log unhandled exceptions.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Initialize trace & correlation IDs
        init_trace_ids()

        # Populate other context variables from request.state
        await set_request_context(request)

        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            # Log the exception asynchronously without breaking the response flow
            await audit_logger.log_exception(
                exc,
                resource=str(request.url),
                debug_details={
                    "method": request.method,
                    "headers": dict(request.headers),
                    "query_params": dict(request.query_params),
                },
            )
            raise  # re-raise for FastAPI exception handlers
