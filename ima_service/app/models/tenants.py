# app/models/tenant.py
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    JSON,
    ForeignKey,
    TIMESTAMP,
    BigInteger,
    text,
    UUID,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from ..db.base_class import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    external_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    schema_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
    )
    plan: Mapped[str | None] = mapped_column(String(64), default="basic")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    source: Mapped[str] = mapped_column(String(64), default="local")
    version: Mapped[int] = mapped_column(BigInteger, default=0)
    last_synced_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))
    deleted_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True))

    # Relationships
    parent: Mapped["Tenant"] = relationship(
        "Tenant", remote_side=[id], backref="children", lazy="selectin"
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="tenant", lazy="selectin"
    )

    def __repr__(self) -> str:
        return (
            f"<Tenant(id={self.id}, name={self.name}, domain={self.domain}, "
            f"schema_name={self.schema_name}, plan={self.plan})>"
        )
