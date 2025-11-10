from enum import Enum

from sqlalchemy import Column, ForeignKey
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

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    user_id = Column(UUID(as_uuid=True), nullable=False)  # from User Service
    tenant_role = Column(SqlEnum(TenantRole), default=TenantRole.VIEWER, nullable=False)
    is_active = Column(SqlEnum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    tenant = relationship("Tenant", back_populates="memberships")
