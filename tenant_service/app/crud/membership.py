"""CRUD operations for TenantMembership model."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from tenant_service.app.models.tenant_membership import TenantMembership, TenantRole
from tenant_service.app.schemas.tenant_membership import (
    TenantMembershipCreate,
    TenantMembershipUpdate,
)

from shared_service.app.models.enums import StatusEnum


class TenantMembershipCRUD:
    """Provides CRUD operations for TenantMembership entities."""

    def get(self, db: Session, membership_id: UUID) -> Optional[TenantMembership]:
        """Retrieve a tenant membership by its unique ID."""
        return (
            db.query(TenantMembership)
            .filter(TenantMembership.id == membership_id)
            .first()
        )

    def get_by_user_and_tenant(
        self, db: Session, user_id: UUID, tenant_id: UUID
    ) -> Optional[TenantMembership]:
        """Get a membership record for a specific user in a tenant."""
        return (
            db.query(TenantMembership)
            .filter(
                TenantMembership.user_id == user_id,
                TenantMembership.tenant_id == tenant_id,
            )
            .first()
        )

    def get_by_tenant(self, db: Session, tenant_id: UUID) -> List[TenantMembership]:
        """Get all memberships for a given tenant."""
        return (
            db.query(TenantMembership)
            .filter(TenantMembership.tenant_id == tenant_id)
            .all()
        )

    def get_by_user(self, db: Session, user_id: UUID) -> List[TenantMembership]:
        """Get all tenant memberships associated with a user."""
        return (
            db.query(TenantMembership).filter(TenantMembership.user_id == user_id).all()
        )

    def create(self, db: Session, obj_in: TenantMembershipCreate) -> TenantMembership:
        """Create a new tenant membership."""
        db_obj = TenantMembership(
            tenant_id=obj_in.tenant_id,
            user_id=obj_in.user_id,
            tenant_role=obj_in.tenant_role or TenantRole.VIEWER,
            is_active=obj_in.is_active or StatusEnum.ACTIVE,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: TenantMembership, obj_in: TenantMembershipUpdate
    ) -> TenantMembership:
        """Update membership details such as role or status."""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, membership_id: UUID) -> Optional[TenantMembership]:
        """Delete a tenant membership by ID."""
        db_obj = self.get(db, membership_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def promote_to_admin(
        self, db: Session, membership_id: UUID
    ) -> Optional[TenantMembership]:
        """Promote a member to admin."""
        membership = self.get(db, membership_id)
        if membership:
            membership.tenant_role = TenantRole.ADMIN
            db.commit()
            db.refresh(membership)
        return membership

    def deactivate(
        self, db: Session, membership_id: UUID
    ) -> Optional[TenantMembership]:
        """Deactivate a tenant membership."""
        membership = self.get(db, membership_id)
        if membership:
            membership.is_active = StatusEnum.INACTIVE
            db.commit()
            db.refresh(membership)
        return membership

    def activate(self, db: Session, membership_id: UUID) -> Optional[TenantMembership]:
        """Activate a tenant membership."""
        membership = self.get(db, membership_id)
        if membership:
            membership.is_active = StatusEnum.ACTIVE
            db.commit()
            db.refresh(membership)
        return membership

    def count_by_tenant(self, db: Session, tenant_id: UUID) -> int:
        """Return total number of members in a tenant."""
        return (
            db.query(TenantMembership)
            .filter(TenantMembership.tenant_id == tenant_id)
            .count()
        )

    def get_active_members(
        self, db: Session, tenant_id: UUID
    ) -> List[TenantMembership]:
        """Return only active members of a tenant."""
        return (
            db.query(TenantMembership)
            .filter(
                TenantMembership.tenant_id == tenant_id,
                TenantMembership.is_active == StatusEnum.ACTIVE,
            )
            .all()
        )


tenant_membership_crud = TenantMembershipCRUD()
