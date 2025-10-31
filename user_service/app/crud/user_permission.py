"""CRUD operations for the UserPermission model."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user_permission import UserPermission


class UserPermissionCRUD:
    """Provides CRUD operations for UserPermission entities."""

    def get(self, db: Session, user_permission_id: UUID) -> Optional[UserPermission]:
        """Retrieve a user-permission mapping by its unique ID."""
        return db.query(UserPermission).filter(UserPermission.id == user_permission_id).first()

    def get_by_user_permission(
        self, db: Session, user_id: UUID, permission_id: UUID
    ) -> Optional[UserPermission]:
        """Retrieve a specific user-permission relationship by user and permission IDs."""
        return (
            db.query(UserPermission)
            .filter(
                UserPermission.user_id == user_id,
                UserPermission.permission_id == permission_id,
            )
            .first()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserPermission]:
        """Return a paginated list of all user-permission relationships."""
        return db.query(UserPermission).offset(skip).limit(limit).all()

    # def create(self, db: Session, obj_in: UserPermissionCreate) -> Optional[UserPermission]:
    #     """Create a new user-permission relationship, avoiding duplicates."""


user_permission_crud = UserPermissionCRUD()
