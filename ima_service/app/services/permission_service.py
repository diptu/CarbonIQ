# app/services/permission_service.py
"""Permission-related business logic for IMA Service."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.permission import Permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionService:
    """Service class to handle Permission CRUD operations."""

    def __init__(self, db: Session):
        self.db = db

    # -------------------------
    # Create Permission
    # -------------------------
    def create_permission(self, permission_in: PermissionCreate) -> Permission:
        permission = Permission(
            name=permission_in.name, description=permission_in.description
        )
        self.db.add(permission)
        try:
            self.db.commit()
            self.db.refresh(permission)
        except IntegrityError:
            self.db.rollback()
            raise ValueError(
                f"Permission with name '{permission_in.name}' already exists."
            )
        return permission

    # -------------------------
    # List Permissions (Paginated)
    # -------------------------
    def list_permissions(
        self, skip: int = 0, limit: int = 50
    ) -> tuple[int, List[Permission]]:
        query = self.db.query(Permission).offset(skip).limit(limit)
        items = query.all()
        total = self.db.query(Permission).count()
        return total, items

    # -------------------------
    # Get Permission by ID
    # -------------------------
    def get_permission(self, permission_id: UUID) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.id == permission_id).first()

    # -------------------------
    # Delete Permission
    # -------------------------
    def delete_permission(self, permission_id: UUID) -> bool:
        permission = self.get_permission(permission_id)
        if not permission:
            return False
        self.db.delete(permission)
        self.db.commit()
        return True
