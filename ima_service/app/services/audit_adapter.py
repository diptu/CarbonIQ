"""Audit adapter for IMA Service.

Provides a reusable audit logging mechanism for all services.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Optional, Union

from ..core.logger import logger

# Callable type for audit events: can be sync or async
AuditCallable = Callable[[Dict[str, Any]], Union[None, Awaitable[None]]]


class AuditAdapter:
    """Adapter to handle audit events consistently for all services."""

    def __init__(self, audit_callable: Optional[AuditCallable] = None) -> None:
        """
        Initialize the AuditAdapter.

        Parameters
        ----------
        audit_callable : Optional[AuditCallable]
            A callable to handle audit events asynchronously or synchronously.
        """
        self._audit_callable: Optional[AuditCallable] = audit_callable

    async def log_event(self, event: Dict[str, Any]) -> None:
        """
        Log an audit event asynchronously.

        If an audit callable is provided, use it; otherwise, fallback to the default logger.

        Parameters
        ----------
        event : Dict[str, Any]
            The audit event data.
        """
        if self._audit_callable:
            result = self._audit_callable(event)
            if result is not None and hasattr(result, "__await__"):
                await result  # type: ignore
        else:
            logger.info("AUDIT EVENT: %s", event)

    async def log(  # pylint:disable=R0913
        self,
        *,
        actor_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        action: str,
        resource: str,
        status: int,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Construct and log an audit event with standard metadata.

        Parameters
        ----------
        actor_id : Optional[str]
            The ID of the actor performing the action.
        tenant_id : Optional[str]
            The ID of the tenant.
        action : str
            The action performed (e.g., "login", "create").
        resource : str
            The resource being acted upon.
        status : int
            Status code of the action (e.g., 200, 401).
        meta : Optional[Dict[str, Any]]
            Additional metadata.
        """
        event: Dict[str, Any] = {
            "actor_id": actor_id,
            "tenant_id": tenant_id,
            "action": action,
            "resource": resource,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "meta": meta or {},
        }
        await self.log_event(event)
