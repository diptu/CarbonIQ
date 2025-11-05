import httpx
from fastapi import Request
from shared_service.app.core.config import settings
from starlette.middleware.base import BaseHTTPMiddleware

AUDIT_SERVICE_URL = settings.AUDIT_SERVICE_URL  # e.g. http://audit-log-service:8000/audit


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically log each request to the Audit Log Service.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Collect metadata
        current_user = getattr(request.state, "current_user", {})
        audit_data = {
            "trace_id": getattr(request.state, "trace_id", None),
            "correlation_id": getattr(request.state, "correlation_id", None),
            "user_id": current_user.get("user_id"),
            "tenant_id": current_user.get("tenant_id"),
            "roles": current_user.get("roles", []),
            "permissions": current_user.get("permissions", []),
            "action": f"{request.method} {request.url.path}",
            "resource": request.url.path,
            "metadata": {
                "status_code": response.status_code,
                "client": request.client.host,
            },
        }

        # Send async request to Audit Log Service
        async with httpx.AsyncClient() as client:
            try:
                await client.post(AUDIT_SERVICE_URL, json=audit_data, timeout=2.0)
            except Exception as e:
                # Avoid failing main request if audit logging fails
                print(f"[AuditMiddleware] Failed to log audit: {e}")

        return response
