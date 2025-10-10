# app/services/user_service.py
from app.services.base_service import BaseService, log_method_call, log_action
from app.models.user import User


class UserService(BaseService[User]):
    @log_method_call
    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        log_action(
            event_name="create_user",
            metadata={"user_id": str(user.id), "email": user.email},
            tenant_id=self.tenant_id,
        )
        return user

    @log_method_call
    def activate_user(self, user: User) -> User:
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        log_action(
            event_name="activate_user",
            metadata={"user_id": str(user.id), "email": user.email},
            tenant_id=self.tenant_id,
        )
        return user

    @log_method_call
    def deactivate_user(self, user: User) -> User:
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        log_action(
            event_name="deactivate_user",
            metadata={"user_id": str(user.id), "email": user.email},
            tenant_id=self.tenant_id,
        )
        return user
