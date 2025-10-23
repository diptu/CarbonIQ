# app/core/audit_adapter.py
from __future__ import annotations
import logging
import traceback
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Optional, Union
import asyncio

from .logger import logger, get_audit_level
from .context import (
    get_user_id,
    get_tenant_id,
    get_trace_id,
    get_correlation_id,
)

# ------------------------------
# Types
# ------------------------------
AuditCallable = Callable[[Dict[str, Any]], Union[None, Awaitable[None]]]


# ------------------------------
# Audit Adapter
# ------------------------------
class AuditAdapter:
    """
    Audit logging adapter.

    Can log audit events using the internal logger or a custom async callback.
    Automatically injects context values if not provided explicitly.
    """

    def __init__(self, audit_callable: Optional[AuditCallable] = None) -> None:
        self._audit_callable = audit_callable

    async def log_event(
        self, event: Dict[str, Any], debug_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a single audit event.

        If debug_details are provided and logger is in DEBUG, they are included.
        Uses either the custom audit_callable or the internal JSON logger.
        """
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
                if asyncio.iscoroutine(result):
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
        """
        Build and log an audit event using context defaults if values not provided.

        Args:
            actor_id: ID of the actor (defaults to context user_id)
            tenant_id: ID of tenant (defaults to context tenant_id)
            action: Name of the action performed
            resource: Resource acted upon
            status: HTTP-like status code
            meta: Optional dictionary of extra metadata
            debug_details: Optional dictionary of debug info
        """
        event: Dict[str, Any] = {
            "actor_id": actor_id or get_user_id(),
            "tenant_id": tenant_id or get_tenant_id(),
            "trace_id": get_trace_id(),
            "correlation_id": get_correlation_id(),
            "action": action,
            "resource": resource,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "meta": meta or {},
        }

        await self.log_event(event, debug_details=debug_details)


# ------------------------------
# Default adapter instance
# ------------------------------
audit_logger = AuditAdapter()
