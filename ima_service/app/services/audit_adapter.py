from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Optional, Union
from contextvars import ContextVar
from ..core.logger import logger

# Type for sync or async audit callables
AuditCallable = Callable[[Dict[str, Any]], Union[None, Awaitable[None]]]

# Context variables for automatic context injection
current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)
current_tenant_id: ContextVar[Optional[str]] = ContextVar("current_tenant_id", default=None)
current_trace_id: ContextVar[Optional[str]] = ContextVar("current_trace_id", default=None)
current_correlation_id: ContextVar[Optional[str]] = ContextVar(
    "current_correlation_id", default=None
)


class AuditAdapter:
    """Consistent audit logging with context-aware metadata."""

    def __init__(self, audit_callable: Optional[AuditCallable] = None) -> None:
        self._audit_callable = audit_callable

    async def log_event(self, event: Dict[str, Any]) -> None:
        """Send audit event to callable or default logger."""
        if self._audit_callable:
            result = self._audit_callable(event)
            if hasattr(result, "__await__"):
                await result
        else:
            logger.info("AUDIT EVENT: %s", event)

    async def log(
        self,
        *,
        actor_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        action: str,
        resource: str,
        status: int,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Standardized log interface with auto context injection."""
        event: Dict[str, Any] = {
            "actor_id": actor_id or current_user_id.get(),
            "tenant_id": tenant_id or current_tenant_id.get(),
            "trace_id": current_trace_id.get(),
            "correlation_id": current_correlation_id.get(),
            "action": action,
            "resource": resource,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "meta": meta or {},
        }
        await self.log_event(event)
