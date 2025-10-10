# app/services/rbac_service.py
from app.services.base_service import BaseService, log_method_call, log_action
from app.models.role import Role
from app.models.permission import Permission


class RBACService(BaseService[Role]):
    @log_method_call
    def assign_permission(self, role: Role, permission: Permission) -> None:
        role.permissions.append(permission)
        self.db.commit()
        log_action(
            event_name="assign_permission_to_role",
            metadata={"role_id": str(role.id), "permission_id": str(permission.id)},
            tenant_id=self.tenant_id,
        )

    @log_method_call
    def revoke_permission(self, role: Role, permission: Permission) -> None:
        if permission in role.permissions:
            role.permissions.remove(permission)
            self.db.commit()
            log_action(
                event_name="revoke_permission_from_role",
                metadata={"role_id": str(role.id), "permission_id": str(permission.id)},
                tenant_id=self.tenant_id,
            )
