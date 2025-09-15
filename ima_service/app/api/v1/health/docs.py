"""
FILE: app/api/v1/health/docs.py
Simple OpenAPI kwargs for health routes.
"""

from __future__ import annotations

from types import SimpleNamespace

HEALTH_DOCS = SimpleNamespace(
    server={
        "summary": "Server Health Check",
        "description": "Check if the API server is reachable.",
        "tags": ["health"],
        "openapi_extra": {"operationId": "healthServer"},
    },
    database={
        "summary": "Database Health Check",
        "description": "Check connectivity to the PostgreSQL database.",
        "tags": ["health"],
        "openapi_extra": {"operationId": "healthDatabase"},
    },
    redis={
        "summary": "Redis Health Check",
        "description": "Check connectivity to the Redis cache.",
        "tags": ["health"],
        "openapi_extra": {"operationId": "healthRedis"},
    },
    full={
        "summary": "Full System Health Check",
        "description": "Run server + database + redis checks.",
        "tags": ["health"],
        "openapi_extra": {"operationId": "healthFull"},
    },
)

# Back-compat names used by router
SERVER_HEALTH_DOCS = HEALTH_DOCS.server
DATABASE_HEALTH_DOCS = HEALTH_DOCS.database
REDIS_HEALTH_DOCS = HEALTH_DOCS.redis
FULL_HEALTH_DOCS = HEALTH_DOCS.full
