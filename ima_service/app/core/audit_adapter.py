from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Optional, Union
from contextvars import ContextVar
import traceback
import asyncio
from .logger import logger, get_audit_level

AuditCallable = Callable[[Dict[str, Any]], Union[None, Awaitable[None]]]

# ContextVars
current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)
current_email: ContextVar[Optional[str]] = ContextVar("current_email", default=None)
current_roles: ContextVar[list[str]] = ContextVar("current_roles", default=[])
current_permissions: ContextVar[list[str]] = ContextVar("current_permissions", default=[])
current_tenant_id: ContextVar[Optional[str]] = ContextVar("current_tenant_id", default=None)
current_trace_id: ContextVar[Optional[str]] = ContextVar("current_trace_id", default=None)
current_correlation_id: ContextVar[Optional[str]] = ContextVar(
    "current_correlation_id", default=None
)


class AuditAdapter:
    def __init__(self, audit_callable: Optional[AuditCallable] = None) -> None:
        self._audit_callable = audit_callable

    async def log_event(
        self, event: Dict[str, Any], debug_details: Optional[Dict[str, Any]] = None
    ) -> None:
        try:
            level = get_audit_level(event.get("action"), event.get("status", 0))
        except Exception:
            level = logging.INFO

        message = event.copy()
        if debug_details and logger.isEnabledFor(logging.DEBUG):
            message["debug_details"] = debug_details

        try:
            if self._audit_callable:
                result = self._audit_callable(message)
                if hasattr(result, "__await__"):
                    await result
            else:
                logger.log(level, "", extra={"extra": message})
        except Exception:
            logger.error(
                f"Failed to log audit event: {message}\nTraceback: {traceback.format_exc()}"
            )

    async def log(
        self,
        *,
        actor_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        action: str,
        resource: str,
        status: int,
        meta: Optional[Dict[str, Any]] = None,
        debug_details: Optional[Dict[str, Any]] = None,
    ) -> None:
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
        await self.log_event(event, debug_details=debug_details)


audit_logger = AuditAdapter()
