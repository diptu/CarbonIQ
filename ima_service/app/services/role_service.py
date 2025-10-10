# app/services/role_service.py
from app.services.base_service import BaseService, log_method_call, log_action
from app.models.role import Role


class RoleService(BaseService[Role]):
    @log_method_call
    def create_role(self, role: Role) -> Role:
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        log_action(
            event_name="create_role",
            metadata={"role_id": str(role.id), "name": role.name},
            tenant_id=self.tenant_id,
        )
        return role

    @log_method_call
    def delete_role(self, role: Role) -> None:
        self.db.delete(role)
        self.db.commit()
        log_action(
            event_name="delete_role",
            metadata={"role_id": str(role.id), "name": role.name},
            tenant_id=self.tenant_id,
        )
