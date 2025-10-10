# # app/services/user_service.py
# """User service with tenant-aware CRUD, activation, and audit logging."""

# from typing import Optional

# from app.models.user import User
# from app.services.base_service import BaseService, log_method_call, log_action


# class UserService(BaseService[User]):
#     """Service for user CRUD and management within a tenant context."""

#     @log_method_call
#     def get_by_email(self, email: str) -> Optional[User]:
#         """Fetch user by email within tenant context."""
#         return (
#             self.db.query(User)
#             .filter(User.email == email, User.tenant_id == self.tenant_id)
#             .first()
#         )

#     @log_method_call
#     def activate_user(self, user: User) -> User:
#         """Activate a user account."""
#         user.is_active = True
#         self.db.commit()
#         self.db.refresh(user)

#         # Log audit action
#         log_action(
#             event_name="activate_user",
#             metadata={"user_id": str(user.id), "email": user.email},
#             tenant_id=self.tenant_id,
#         )
#         return user

#     @log_method_call
#     def deactivate_user(self, user: User) -> User:
#         """Deactivate a user account."""
#         user.is_active = False
#         self.db.commit()
#         self.db.refresh(user)

#         log_action(
#             event_name="deactivate_user",
#             metadata={"user_id": str(user.id), "email": user.email},
#             tenant_id=self.tenant_id,
#         )
#         return user

#     @log_method_call
#     def update_user(self, user: User) -> User:
#         """Update user details and commit changes."""
#         self.db.commit()
#         self.db.refresh(user)

#         log_action(
#             event_name="update_user",
#             metadata={"user_id": str(user.id), "email": user.email},
#             tenant_id=self.tenant_id,
#         )
#         return user

#     @log_method_call
#     def delete_user(self, user: User) -> None:
#         """Delete user account."""
#         self.db.delete(user)
#         self.db.commit()

#         log_action(
#             event_name="delete_user",
#             metadata={"user_id": str(user.id), "email": user.email},
#             tenant_id=self.tenant_id,
#         )
