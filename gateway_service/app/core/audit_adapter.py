from functools import wraps

import httpx
from app.core.config import settings

AUDIT_SERVICE_URL = settings.AUDIT_SERVICE_URL


def audit_action(action: str, resource: str = None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response = action(*args, **kwargs)

            # Extract FastAPI request from kwargs
            request = kwargs.get("request")
            if request:
                current_user = getattr(request.state, "current_user", {})
                audit_data = {
                    "trace_id": getattr(request.state, "trace_id", None),
                    "correlation_id": getattr(request.state, "correlation_id", None),
                    "user_id": current_user.get("user_id"),
                    "tenant_id": current_user.get("tenant_id"),
                    "roles": current_user.get("roles", []),
                    "permissions": current_user.get("permissions", []),
                    "action": action,
                    "resource": resource or request.url.path,
                    "metadata": {"status_code": response.status_code},
                }
                async with httpx.AsyncClient() as client:
                    try:
                        await client.post(
                            AUDIT_SERVICE_URL, json=audit_data, timeout=2.0
                        )
                    except Exception as e:
                        print(f"[audit_action] Failed to log audit: {e}")
            return response

        return wrapper

    return decorator
