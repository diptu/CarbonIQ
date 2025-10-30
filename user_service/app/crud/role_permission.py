"""CRUD operations for the RolePermission model."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.role_permission import RolePermission
from app.schemas.role_permission import RolePermissionCreate


class RolePermissionCRUD:
    """Provides CRUD operations for RolePermission entities."""

    def get(self, db: Session, role_permission_id: UUID):
        """Retrieve a role-permission mapping by its unique ID."""
        return db.query(RolePermission).filter(RolePermission.id == role_permission_id).first()

    def get_by_role_permission(self, db: Session, role_id: UUID, permission_id: UUID):
        """Retrieve a specific role-permission relationship by role and permission IDs."""
        return (
            db.query(RolePermission)
            .filter(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
            .first()
        )

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        """Return a paginated list of all role-permission relationships."""
        return db.query(RolePermission).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: RolePermissionCreate):
        """Create a new role-permission relationship, avoiding duplicates."""
        existing = self.get_by_role_permission(db, obj_in.role_id, obj_in.permission_id)
        if existing:
            return existing
        db_obj = RolePermission(role_id=obj_in.role_id, permission_id=obj_in.permission_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, role_permission_id: UUID):
        """Delete a role-permission relationship by its ID."""
        db_obj = self.get(db, role_permission_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj


role_permission_crud = RolePermissionCRUD()
