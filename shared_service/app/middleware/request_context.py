# middleware/request_context.py
import json
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Adds trace/correlation IDs, measures request duration, and injects request_duration_ms into JSON responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # ---- Setup context ----
        request.state.trace_id = str(uuid.uuid4())
        request.state.correlation_id = request.headers.get(
            "X-Correlation-ID", str(uuid.uuid4())
        )
        request.state.user_id = request.headers.get("X-User-ID")
        request.state.tenant_id = request.headers.get("X-Tenant-ID")
        request.state.roles = []
        request.state.permissions = []

        # ---- Timer start ----
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        request.state.request_duration_ms = duration_ms

        # ---- Add trace headers ----
        response.headers["X-Trace-ID"] = request.state.trace_id
        response.headers["X-Correlation-ID"] = request.state.correlation_id

        # ---- JSON response: inject duration into meta ----
        content_type = response.headers.get("content-type", "")

        if "application/json" in content_type:
            try:
                # extract original body
                body = b"".join([chunk async for chunk in response.body_iterator])
                payload = json.loads(body)

                if isinstance(payload, dict):
                    payload.setdefault("meta", {})
                    payload["meta"]["request_duration_ms"] = duration_ms

                # rebuild JSON response
                new_response = JSONResponse(
                    content=payload,
                    status_code=response.status_code,
                )

                # preserve headers
                for header, value in response.headers.items():
                    if header.lower() not in ("content-length", "content-type"):
                        new_response.headers[header] = value

                response = new_response

            except Exception as e:
                print(f"[RequestContext] Failed to inject duration: {e}")

        else:
            # Non-JSON: add header only
            response.headers["X-Request-Duration-Ms"] = str(duration_ms)

        return response
