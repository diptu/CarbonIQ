"""CRUD operations for TenantDomain model."""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from tenant_service.app.models.domain import TenantDomain
from tenant_service.app.models.tenant import Tenant
from tenant_service.app.schemas.domain import TenantDomainCreate, TenantDomainUpdate


class TenantDomainCRUD:
    """Provides CRUD operations for TenantDomain entities."""

    def get(self, db: Session, domain_id: UUID) -> Optional[TenantDomain]:
        """Retrieve a domain by its unique ID."""
        return db.query(TenantDomain).filter(TenantDomain.id == domain_id).first()

    def get_by_domain(self, db: Session, domain: str) -> Optional[TenantDomain]:
        """Retrieve a tenant domain by the domain name."""
        return db.query(TenantDomain).filter(TenantDomain.domain == domain).first()

    def get_by_tenant(self, db: Session, tenant_id: UUID) -> List[TenantDomain]:
        """List all domains associated with a given tenant."""
        return db.query(TenantDomain).filter(TenantDomain.tenant_id == tenant_id).all()

    def create(self, db: Session, obj_in: TenantDomainCreate) -> TenantDomain:
        """Create and attach a new domain to a tenant."""
        # Ensure the tenant exists
        tenant = db.query(Tenant).filter(Tenant.id == obj_in.tenant_id).first()
        if not tenant:
            raise ValueError("Tenant not found")

        db_obj = TenantDomain(
            tenant_id=obj_in.tenant_id,
            domain=obj_in.domain.lower(),
            is_verified=False,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: TenantDomain, obj_in: TenantDomainUpdate
    ) -> Optional[TenantDomain]:
        """Update domain details (e.g., verification status)."""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, domain_id: UUID) -> Optional[TenantDomain]:
        """Delete a domain record."""
        db_obj = self.get(db, domain_id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def verify(self, db: Session, domain_id: UUID) -> Optional[TenantDomain]:
        """Mark a domain as verified (e.g., DNS or TXT verification passed)."""
        domain = self.get(db, domain_id)
        if domain:
            domain.is_verified = True
            db.commit()
            db.refresh(domain)
        return domain

    def unverify(self, db: Session, domain_id: UUID) -> Optional[TenantDomain]:
        """Unverify a domain (e.g., failed validation or domain transfer)."""
        domain = self.get(db, domain_id)
        if domain:
            domain.is_verified = False
            db.commit()
            db.refresh(domain)
        return domain

    def count(self, db: Session) -> int:
        """Return total number of registered domains."""
        return db.query(TenantDomain).count()


tenant_domain_crud = TenantDomainCRUD()
