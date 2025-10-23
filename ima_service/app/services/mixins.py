# services/mixins.py
# app/services/mixins.py
"""
SecuredServiceMixin

This mixin provides a reusable pattern for enforcing RBAC (role-based access control)
and audit logging in service-layer operations.

It is intended to be used in combination with BaseService or any of its derivatives.
By using this mixin, services can:

- Perform permission checks automatically before executing any business logic.
- Wrap database operations with consistent audit logging.
- Standardize error handling and status reporting across services.
- Reduce boilerplate code in tenant-scoped, RBAC-secured services.

Example usage:

    class BillingService(SecuredServiceMixin, BaseService):
        async def list(self, model, limit=100, offset=0):
            return await self._execute(
                "billing:list",
                model.__name__,
                lambda: self.db.execute(
                    self.scope_query(select(model).limit(limit).offset(offset))
                ).then(lambda r: list(r.scalars().all()))
            )

Attributes:
    None
"""

from .base_service import BaseService


class SecuredServiceMixin(BaseService):
    async def _pre_check(self, permission: str) -> None:
        await self.rbac_service.check_access(
            self.current_user_id, permission, self.current_tenant_id
        )

    async def _execute(self, action: str, resource: str, db_op: callable) -> any:
        await self._pre_check(action)
        status = 200
        try:
            return await db_op()
        except Exception as e:
            status = 500
            raise
        finally:
            await self._audit(
                action=action,
                resource=resource,
                status=status,
                meta={"user_id": self.current_user_id},
            )
