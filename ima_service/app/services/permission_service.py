# app/services/permission_service.py
from app.services.base_service import BaseService, log_method_call, log_action
from app.models.permission import Permission


class PermissionService(BaseService[Permission]):
    @log_method_call
    def add_permission(self, permission: Permission) -> Permission:
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        log_action(
            event_name="add_permission",
            metadata={"permission_id": str(permission.id), "name": permission.name},
            tenant_id=self.tenant_id,
        )
        return permission

    @log_method_call
    def remove_permission(self, permission: Permission) -> None:
        self.db.delete(permission)
        self.db.commit()
        log_action(
            event_name="remove_permission",
            metadata={"permission_id": str(permission.id), "name": permission.name},
            tenant_id=self.tenant_id,
        )
