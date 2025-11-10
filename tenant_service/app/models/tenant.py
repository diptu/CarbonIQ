import re

from sqlalchemy import Column, String, event, text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import relationship

from shared_service.app.models.enums import PlanEnum, StatusEnum
from tenant_service.app.models.base import BaseModel


class Tenant(BaseModel):
    __tablename__ = "tenants"

    name = Column(String(255), nullable=False, unique=False)
    slug = Column(String(255), unique=True, nullable=False)

    status = Column(SqlEnum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    plan = Column(SqlEnum(PlanEnum), default=PlanEnum.FREE, nullable=False)

    memberships = relationship("TenantMembership", back_populates="tenant")
    domains = relationship("TenantDomain", back_populates="tenant")


# --------------------------
# Event listener for unique slug
# --------------------------
@event.listens_for(Tenant, "before_insert")
def generate_unique_slug(mapper, connection, target: Tenant):
    """
    Automatically generate a unique slug from the name before insert.
    """
    if target.slug:
        # Slug already provided, skip
        return

    base_slug = re.sub(r"[^a-zA-Z0-9]+", "_", target.name.lower()).strip("_")
    slug = base_slug
    counter = 1

    # Check for uniqueness
    while True:
        result = connection.execute(
            text("SELECT 1 FROM tenants WHERE slug = :slug LIMIT 1"),
            {"slug": slug},
        ).first()
        if not result:
            break
        slug = f"{base_slug}_{counter}"
        counter += 1

    target.slug = slug
