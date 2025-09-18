# FILE: ima_service/app/api/v1/health/services/base.py
"""
Shared runner utilities + color-coded logging for health services.
"""

from __future__ import annotations

import logging
from typing import Awaitable, Callable, Final

from ..schemas import HealthCheckResponse
from ..utils import HealthService

CheckFn = Callable[[], Awaitable[bool]]

# Color codes (kept local to avoid global logging side-effects)
RESET: Final = "\033[0m"
RED: Final = "\033[31m"
YELLOW: Final = "\033[33m"
GREEN: Final = "\033[32m"
CYAN: Final = "\033[36m"

LOG = logging.getLogger(__name__)


async def run_check(
    name: str,
    check_fn: CheckFn,
    *,
    timeout: float = 2.0,
    key: str | None = None,
) -> HealthCheckResponse:
    """Run a single health check with standardized formatting."""
    resp = await HealthService(name=name, check_fn=check_fn, key=key, timeout=timeout)()
    color = GREEN if resp.status == "success" else (YELLOW if resp.code == 503 else RED)
    LOG.info("%s%s%s: %s", color, name, RESET, resp.message)
    if resp.details:
        LOG.debug("%s%s details%s: %s", CYAN, name, RESET, resp.details)
    return resp
