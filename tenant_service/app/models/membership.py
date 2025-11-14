from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, ForeignKey
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from shared_service.app.models.enums import StatusEnum
from tenant_service.app.models.base import BaseModel


class TenantRole(str, Enum):
    """Predefined roles for tenant-level RBAC."""

    OWNER = "owner"
    ADMIN = "admin"
    BILLING_ADMIN = "billing_admin"
    MEMBER = "member"
    VIEWER = "viewer"
    GUEST = "guest"


class TenantMembership(BaseModel):
    __tablename__ = "tenant_memberships"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)  # reference User Service
    tenant_role = Column(SqlEnum(TenantRole), default=TenantRole.VIEWER, nullable=False)
    is_active = Column(SqlEnum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    has_parent_access = Column(
        Boolean, default=False, nullable=False
    )  # True if user can access child tenants
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="memberships")

    def __repr__(self):
        return f"<TenantMembership user_id={self.user_id} \
            tenant_id={self.tenant_id}, role={self.tenant_role}>"
