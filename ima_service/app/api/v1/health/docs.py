# ruff: noqa: D401
"""
FILE: app/api/v1/health/docs.py
Build per-route kwargs for FastAPI while unsupported OpenAPI keys
(e.g., operationId) are routed via `openapi_extra`.
"""

from __future__ import annotations

from functools import cached_property
from typing import Any, Callable, Dict, Optional, TypedDict

FASTAPI_ROUTE_KWARGS: frozenset[str] = frozenset(
    {
        "summary",
        "description",
        "tags",
        "deprecated",
        "response_model",
        "responses",
        "status_code",
        "openapi_extra",
    }
)


class RouteKwargs(TypedDict, total=False):
    """Typed kwargs container for FastAPI route decorators."""

    summary: str
    description: str
    tags: list[str]
    deprecated: bool
    response_model: Any
    responses: Dict[int, Any]
    status_code: int
    openapi_extra: Dict[str, Any]


def _to_route_kwargs(base: Dict[str, Any]) -> RouteKwargs:
    """Filter an arbitrary dict down to FastAPI-supported kwargs.

    Unsupported keys are ignored unless they belong in `openapi_extra`.
    """
    kwargs: RouteKwargs = {}
    extra: Dict[str, Any] = dict(base.get("openapi_extra", {}))

    if "operationId" in base:
        extra["operationId"] = base["operationId"]
    if "operation_id" in base:
        extra["operationId"] = base["operation_id"]

    for key, val in base.items():
        if key in {"operationId", "operation_id", "openapi_extra"}:
            continue
        if key in FASTAPI_ROUTE_KWARGS:
            kwargs[key] = val  # type: ignore[index]

    if extra:
        kwargs["openapi_extra"] = extra

    return kwargs


def openapi_doc(
    summary: str,
    description: str,
    **static_extras: Any,
) -> cached_property:
    """Return a cached property of FastAPI route kwargs.

    Parameters
    ----------
    summary : str
        Short summary for the endpoint.
    description : str
        Longer human-readable description.
    **static_extras : Any
        Additional static fields (e.g., tags, responses). Unsupported keys
        are moved into `openapi_extra`.
    """

    def decorator(
        fn: Callable[[Any], Optional[Dict[str, Any]]],
    ) -> cached_property:
        @cached_property
        def wrapper(self: Any) -> RouteKwargs:
            base: Dict[str, Any] = {
                "summary": summary,
                "description": description,
            }
            if static_extras:
                base.update(static_extras)
            dynamic = fn(self) or {}
            if dynamic:
                base.update(dynamic)
            return _to_route_kwargs(base)

        return wrapper

    return decorator


class HealthDocs:
    """Container for health endpoint OpenAPI docs (cached + typed)."""

    default_tags: tuple[str, ...] = ("health",)

    @openapi_doc(
        summary="Server Health Check",
        description="Check if the API server is reachable.",
    )
    def server(self) -> Optional[Dict[str, Any]]:
        """OpenAPI kwargs for the `/health/server` endpoint."""
        return {"tags": list(self.default_tags), "operationId": "healthServer"}

    @openapi_doc(
        summary="Database Health Check",
        description="Check connectivity to the PostgreSQL database.",
    )
    def database(self) -> Optional[Dict[str, Any]]:
        """OpenAPI kwargs for the `/health/database` endpoint."""
        return {
            "tags": list(self.default_tags),
            "operationId": "healthDatabase",
        }

    @openapi_doc(
        summary="Redis Health Check",
        description="Check connectivity to the Redis cache.",
    )
    def redis(self) -> Optional[Dict[str, Any]]:
        """OpenAPI kwargs for the `/health/redis` endpoint."""
        return {"tags": list(self.default_tags), "operationId": "healthRedis"}

    @openapi_doc(
        summary="Full System Health Check",
        description="Run combined checks for server, database, and Redis.",
    )
    def full(self) -> Optional[Dict[str, Any]]:
        """OpenAPI kwargs for the `/health/full` endpoint."""
        return {"tags": list(self.default_tags), "operationId": "healthFull"}

    @cached_property
    def all(self) -> Dict[str, RouteKwargs]:
        """Grouped, cached view over all endpoint docs."""
        return {
            "server": self.server,
            "database": self.database,
            "redis": self.redis,
            "full": self.full,
        }


HEALTH_DOCS = HealthDocs()

# Back-compat constants
SERVER_HEALTH_DOCS = HEALTH_DOCS.server
DATABASE_HEALTH_DOCS = HEALTH_DOCS.database
REDIS_HEALTH_DOCS = HEALTH_DOCS.redis
FULL_HEALTH_DOCS = HEALTH_DOCS.full
