"""Standard response envelope shared across all CarbonIQ services.

Success: {"success": true, "data": ..., "meta": {"request_id", "timestamp"}}
Failure: {"success": false, "error": {"code", "message"}, "meta": {...}}

See services/iam-service/example_api.md and services/tenant-service/example_api.md
for the reference shape this mirrors.
"""

import uuid
from datetime import UTC, datetime
from typing import Any


def _meta(request_id: str | None = None) -> dict[str, str]:
    return {
        "request_id": request_id or f"req_{uuid.uuid4().hex[:12]}",
        "timestamp": datetime.now(UTC).isoformat(),
    }


def success_envelope(data: Any, request_id: str | None = None) -> dict[str, Any]:
    return {"success": True, "data": data, "meta": _meta(request_id)}


def error_envelope(
    code: str, message: str, request_id: str | None = None
) -> dict[str, Any]:
    return {
        "success": False,
        "error": {"code": code, "message": message},
        "meta": _meta(request_id),
    }
