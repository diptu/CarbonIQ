# app/services/mixins.py
"""
SecuredServiceMixin

Mixin for enforcing RBAC and audit logging in service-layer operations.

Features:
- Automatic RBAC permission checks before executing business logic.
- Wraps async DB operations with consistent audit logging.
- Standardized exception handling and status reporting.
- Optional retry hook for transient errors.
- Reduces boilerplate in tenant-scoped, RBAC-secured services.

Usage:

    class BillingService(SecuredServiceMixin, BaseService):
        async def list(self, model, limit=100, offset=0):
            return await self._execute(
                action="billing:list",
                resource=model.__name__,
                db_op=lambda: self.db.execute(
                    self.scope_query(select(model).limit(limit).offset(offset))
                )
            )
"""

from __future__ import annotations
from typing import Any, Callable, Awaitable, Optional
from .base_service import BaseService


class SecuredServiceMixin(BaseService):
    """
    Mixin for services requiring RBAC enforcement and audit logging.
    Requires `self.rbac_service` to be defined in the derived service.
    """

    async def _pre_check(self, permission: str) -> None:
        """
        Perform RBAC check for the current user and tenant.

        Args:
            permission (str): Permission string to check.

        Raises:
            PermissionError: If the user lacks the required permission.
        """
        if not hasattr(self, "rbac_service"):
            raise AttributeError("rbac_service not defined in service")

        await self.rbac_service.check_access(
            user_id=self.current_user_id,
            permission_code=permission,
            tenant_id=self.current_tenant_id,
        )

    async def _execute(
        self,
        action: str,
        resource: str,
        db_op: Callable[[], Awaitable[Any]],
        retry_on_failure: Optional[int] = 0,
        include_exception_in_audit: bool = True,
    ) -> Any:
        """
        Execute a DB operation with RBAC pre-check and audit logging.

        Args:
            action (str): Action being performed (e.g., 'billing:update').
            resource (str): Name of the resource (e.g., ORM model name).
            db_op (Callable[[], Awaitable[Any]]): Async callable performing the DB operation.
            retry_on_failure (Optional[int]): Number of retries for transient errors (default=0).
            include_exception_in_audit (bool): Include exception details in audit log (default=True).

        Returns:
            Any: Result of the DB operation.

        Raises:
            Exception: Propagates exceptions from the DB operation.
        """
        await self._pre_check(action)
        attempt = 0
        status = 200
        last_exception: Optional[Exception] = None

        while attempt <= retry_on_failure:
            try:
                result = await db_op()
                return result
            except Exception as e:
                last_exception = e
                status = 500
                attempt += 1
                if attempt > retry_on_failure:
                    raise
            finally:
                meta = {"user_id": self.current_user_id}
                if include_exception_in_audit and last_exception:
                    meta["error"] = str(last_exception)
                await self._audit(action=action, resource=resource, status=status, meta=meta)
