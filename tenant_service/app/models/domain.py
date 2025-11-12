from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from tenant_service.app.models.base import BaseModel


class TenantDomain(BaseModel):
    __tablename__ = "tenant_domains"

    tenant_id = Column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )
    domain = Column(String(255), unique=True, nullable=False)
    is_primary = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationship to Tenant; do NOT use cascade here
    tenant = relationship("Tenant", back_populates="domains")

    def __repr__(self):
        return f"<TenantDomain(domain={self.domain}, primary={self.is_primary})>"
