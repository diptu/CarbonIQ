# FILE: ima_service/app/api/v1/health/docs.py
"""
OpenAPI docs metadata for health endpoints (minimal + consistent).
"""

from __future__ import annotations

from typing import Any, Final, Mapping


def _doc(summary: str, desc: str, op_id: str) -> Mapping[str, Any]:
    return {
        "summary": summary,
        "description": desc,
        "tags": ["health"],
        "openapi_extra": {"operationId": op_id},
    }


SERVER_HEALTH_DOCS: Final = _doc(
    "Server Health", "Is the API reachable?", "healthServer"
)
DATABASE_HEALTH_DOCS: Final = _doc(
    "Database Health", "PostgreSQL connectivity.", "healthDatabase"
)
REDIS_HEALTH_DOCS: Final = _doc("Redis Health", "Redis connectivity.", "healthRedis")
FULL_HEALTH_DOCS: Final = _doc(
    "Full Health", "Server + DB + Redis checks.", "healthFull"
)

__all__ = [
    "SERVER_HEALTH_DOCS",
    "DATABASE_HEALTH_DOCS",
    "REDIS_HEALTH_DOCS",
    "FULL_HEALTH_DOCS",
]
