"""CRUD operations for the Permission model."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionCRUD:
    """Provides CRUD operations for Permission entities."""

    def get(self, db: Session, permission_id: UUID):
        """Retrieve a permission by its unique ID."""
        return db.query(Permission).filter(Permission.id == permission_id).first()

    def get_by_name(self, db: Session, name: str):
        """Retrieve a permission by its name."""
        return db.query(Permission).filter(Permission.name == name).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        """Return a paginated list of all permissions."""
        return db.query(Permission).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: PermissionCreate):
        """Create a new permission record."""
        db_obj = Permission(name=obj_in.name, description=obj_in.description)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Permission, obj_in: PermissionUpdate):
        """Update an existing permission's details."""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, permission_id: UUID):
        """Delete a permission by its ID."""
        db_obj = self.get(db, permission_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj


permission_crud = PermissionCRUD()
