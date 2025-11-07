"""CRUD operations for UserRole and RolePermission models."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from user_service.app.models.role_permission import RolePermission
from user_service.app.schemas.role_permission import RolePermissionCreate


# ---------------------
# RolePermission CRUD
# ---------------------
class RolePermissionCRUD:
    """Provides CRUD operations for RolePermission entities."""

    def get(self, db: Session, role_perm_id: UUID) -> Optional[RolePermission]:
        return db.query(RolePermission).filter(RolePermission.id == role_perm_id).first()

    def get_by_role_permission(
        self, db: Session, role_id: UUID, permission_id: UUID
    ) -> Optional[RolePermission]:
        return (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id == role_id, RolePermission.permission_id == permission_id
            )
            .first()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[RolePermission]:
        return db.query(RolePermission).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: RolePermissionCreate) -> RolePermission:
        existing = self.get_by_role_permission(db, obj_in.role_id, obj_in.permission_id)
        if existing:
            return existing

        db_obj = RolePermission(role_id=obj_in.role_id, permission_id=obj_in.permission_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, role_perm_id: UUID) -> Optional[RolePermission]:
        db_obj = self.get(db, role_perm_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def count(self, db: Session) -> int:
        return db.query(RolePermission).count()


role_permission_crud = RolePermissionCRUD()
