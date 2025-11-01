"""CRUD operations for the UserRolePermission association model."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user_role_permission import UserRolePermission
from app.schemas.user_role_permission import UserRolePermissionCreate


class UserRolePermissionCRUD:
    """Provides CRUD operations for UserRolePermission entities."""

    def get(self, db: Session, assignment_id: UUID) -> Optional[UserRolePermission]:
        """Retrieve a specific user-role-permission mapping by ID."""
        return db.query(UserRolePermission).filter(UserRolePermission.id == assignment_id).first()

    def get_by_user_role_permission(
        self, db: Session, user_id: UUID, role_id: UUID, permission_id: UUID
    ) -> Optional[UserRolePermission]:
        """Retrieve a specific mapping using user, role, and permission IDs."""
        return (
            db.query(UserRolePermission)
            .filter(
                UserRolePermission.user_id == user_id,
                UserRolePermission.role_id == role_id,
                UserRolePermission.permission_id == permission_id,
            )
            .first()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserRolePermission]:
        """Return a paginated list of all user-role-permission mappings."""
        return db.query(UserRolePermission).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: UserRolePermissionCreate) -> UserRolePermission:
        """
        Create a new mapping if not already existing.
        Avoids duplicate assignments.
        """
        existing = self.get_by_user_role_permission(
            db, obj_in.user_id, obj_in.role_id, obj_in.permission_id
        )
        if existing:
            return existing

        db_obj = UserRolePermission(
            user_id=obj_in.user_id,
            role_id=obj_in.role_id,
            permission_id=obj_in.permission_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, assignment_id: UUID) -> Optional[UserRolePermission]:
        """Delete a user-role-permission entry by ID."""
        db_obj = self.get(db, assignment_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj


user_role_permission_crud = UserRolePermissionCRUD()
