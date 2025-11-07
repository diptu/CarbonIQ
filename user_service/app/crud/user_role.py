"""CRUD operations for UserRole and RolePermission models."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from user_service.app.models.user_role import UserRole
from user_service.app.schemas.user_role import UserRoleCreate


# ---------------------
# UserRole CRUD
# ---------------------
class UserRoleCRUD:
    """Provides CRUD operations for UserRole entities."""

    def get(self, db: Session, user_role_id: UUID) -> Optional[UserRole]:
        return db.query(UserRole).filter(UserRole.id == user_role_id).first()

    def get_by_user_role(self, db: Session, user_id: UUID, role_id: UUID) -> Optional[UserRole]:
        return (
            db.query(UserRole)
            .filter(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .first()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserRole]:
        return db.query(UserRole).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: UserRoleCreate) -> UserRole:
        existing = self.get_by_user_role(db, obj_in.user_id, obj_in.role_id)
        if existing:
            return existing

        db_obj = UserRole(user_id=obj_in.user_id, role_id=obj_in.role_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, user_role_id: UUID) -> Optional[UserRole]:
        db_obj = self.get(db, user_role_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def count(self, db: Session) -> int:
        return db.query(UserRole).count()


user_role_crud = UserRoleCRUD()
