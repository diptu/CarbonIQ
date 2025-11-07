# pylint: disable=duplicate-code
"""CRUD operations for User model."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from user_service.app.models.role import Role
from user_service.app.schemas.role import RoleCreate, RoleUpdate


class RoleCRUD:
    """Provides CRUD operations for Role entities."""

    def get(self, db: Session, role_id: UUID) -> Optional[Role]:
        """Retrieve a role by their unique ID."""
        return db.query(Role).filter(Role.id == role_id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Role]:
        """Retrieve a role by their name address."""
        return db.query(Role).filter(Role.name == name).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        """Return a paginated list of roles."""
        return db.query(Role).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: RoleCreate) -> Optional[Role]:
        """Create a new role with a hashed password."""
        db_obj = Role(name=obj_in.name, description=obj_in.description)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Role, obj_in: RoleUpdate) -> Optional[Role]:
        """Update an existing roles's details."""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, role_id: UUID) -> Optional[Role]:
        """Remove an existing role."""
        db_obj = self.get(db, role_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def count(self, db: Session) -> int:
        return db.query(Role).count()


role_crud = RoleCRUD()
