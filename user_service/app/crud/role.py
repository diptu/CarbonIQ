"""CRUD operations for User model."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate


class RoleCRUD:
    """Provides CRUD operations for Role entities."""

    def get(self, db: Session, role_id: UUID):
        """Retrieve a role by their unique ID."""
        return db.query(Role).filter(Role.id == role_id).first()

    def get_by_name(self, db: Session, name: str):
        """Retrieve a role by their name address."""
        return db.query(Role).filter(Role.name == name).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        """Return a paginated list of roles."""
        return db.query(Role).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: RoleCreate):
        """Create a new role with a hashed password."""
        db_obj = Role(name=obj_in.name, description=obj_in.description)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Role, obj_in: RoleUpdate):
        """Update an existing roles's details."""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, role_id: UUID):
        """Remove an existing role."""
        db_obj = self.get(db, role_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj


role_crud = RoleCRUD()
