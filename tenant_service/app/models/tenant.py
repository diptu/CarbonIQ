from sqlalchemy import Column, ForeignKey, String, event
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from shared_service.app.models.enums import PlanEnum, StatusEnum
from tenant_service.app.models.base import BaseModel


class Tenant(BaseModel):
    __tablename__ = "tenants"

    name = Column(String(255), nullable=False)
    schema_name = Column(String(255), unique=True, nullable=False)

    parent_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    parent = relationship(
        "Tenant",
        remote_side=lambda: [Tenant.id],  # defer evaluation for self-reference
        backref="children",
    )

    status = Column(SqlEnum(StatusEnum), default=StatusEnum.ACTIVE, nullable=False)
    plan = Column(SqlEnum(PlanEnum), default=PlanEnum.FREE, nullable=False)

    memberships = relationship(
        "TenantMembership",
        back_populates="tenant",
        cascade="all, delete-orphan",
        single_parent=True,
    )
    domains = relationship(
        "TenantDomain",
        back_populates="tenant",
        cascade="all, delete-orphan",  # correct place for delete-orphan
    )

    def __repr__(self):
        return f"<Tenant(name={self.name}, schema={self.schema_name})>"


from sqlalchemy import text


@event.listens_for(Tenant, "before_insert")
def generate_schema_name(mapper, connection, target):
    base_name = target.name.lower().replace(" ", "_").replace(".", "_")

    if target.parent_id:
        parent_schema = connection.execute(
            text("SELECT schema_name FROM tenants WHERE id=:parent_id"),
            {"parent_id": str(target.parent_id)},
        ).scalar()
        if parent_schema:
            base_name = f"{base_name}_{parent_schema}"

    existing = connection.execute(
        text("SELECT COUNT(*) FROM tenants WHERE schema_name=:schema_name"),
        {"schema_name": base_name},
    ).scalar()
    if existing:
        base_name = f"{base_name}_{existing + 1}"

    target.schema_name = base_name
