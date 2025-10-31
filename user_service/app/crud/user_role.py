"""CRUD operations for the UserRole model."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user_role import UserRole
from app.schemas.user_role import UserRoleCreate


class UserRoleCRUD:
    """Provides CRUD operations for UserRole entities."""

    def get(self, db: Session, user_role_id: UUID) -> Optional[UserRole]:
        """Retrieve a user-role mapping by its unique ID."""
        return db.query(UserRole).filter(UserRole.id == user_role_id).first()

    def get_by_user_role(self, db: Session, user_id: UUID, role_id: UUID) -> Optional[UserRole]:
        """Retrieve a specific user-role relationship by user and role IDs."""
        return (
            db.query(UserRole)
            .filter(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
            .first()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserRole]:
        """Return a paginated list of all user-role relationships."""
        return db.query(UserRole).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: UserRoleCreate) -> UserRole:
        """Create a new user-role relationship, avoiding duplicates."""
        existing = self.get_by_user_role(db, obj_in.user_id, obj_in.role_id)
        if existing:
            return existing
        db_obj = UserRole(user_id=obj_in.user_id, role_id=obj_in.role_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, user_role_id: UUID) -> Optional[UserRole]:
        """Delete a user-role relationship by its ID."""
        db_obj = self.get(db, user_role_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj


user_role_crud = UserRoleCRUD()
