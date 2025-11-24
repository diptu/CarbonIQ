from typing import Any, Dict

from fastapi import APIRouter

from .docs import SERVER_HEALTH_DOCS

# --- endpoints remain the same ---

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/server", **SERVER_HEALTH_DOCS)
async def server_health() -> Dict[str, Any]:
    """Liveness check for the API server."""

    async def server_check() -> bool:
        """
        Lightweight internal check.
        Replace/extend this with:
        - CPU/memory threshold checks
        - Internal service checks
        - Dependency readiness (cache, message broker, etc.)
        """
        return True  # Always true unless extended

    is_alive = await server_check()

    return {
        "status": "ok" if is_alive else "error",
        "server": is_alive,
    }
