# app/services/tenant_service.py
from app.services.base_service import BaseService, log_method_call, log_action
from app.models.tenant import Tenant


class TenantService(BaseService[Tenant]):
    @log_method_call
    def create_tenant(self, tenant: Tenant) -> Tenant:
        self.db.add(tenant)
        self.db.commit()
        self.db.refresh(tenant)
        log_action(
            event_name="create_tenant",
            metadata={"tenant_id": str(tenant.id), "name": tenant.name},
            tenant_id=self.tenant_id,
        )
        return tenant

    @log_method_call
    def update_tenant(self, tenant: Tenant, updates: dict) -> Tenant:
        for k, v in updates.items():
            setattr(tenant, k, v)
        self.db.commit()
        self.db.refresh(tenant)
        log_action(
            event_name="update_tenant",
            metadata={"tenant_id": str(tenant.id), "updates": updates},
            tenant_id=self.tenant_id,
        )
        return tenant

    @log_method_call
    def delete_tenant(self, tenant: Tenant) -> None:
        self.db.delete(tenant)
        self.db.commit()
        log_action(
            event_name="delete_tenant",
            metadata={"tenant_id": str(tenant.id)},
            tenant_id=self.tenant_id,
        )
