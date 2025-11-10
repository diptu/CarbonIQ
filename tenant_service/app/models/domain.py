from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from tenant_service.app.models.base import BaseModel


class TenantDomain(BaseModel):
    __tablename__ = "tenant_domains"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    domain = Column(String(255), unique=True, nullable=False)
    is_verified = Column(Boolean, default=False)

    tenant = relationship("Tenant", back_populates="domains")
