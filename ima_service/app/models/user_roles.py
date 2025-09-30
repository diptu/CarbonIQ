"""Association table linking users, roles, and tenants in IAM service."""

from sqlalchemy import Column, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from ..db.base_class import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True),
    Column("tenant_id", UUID(as_uuid=True), nullable=True),
    Column(
        "created_at",
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        server_default=func.now(),  # pylint: disable=not-callable
        onupdate=func.now(),  # pylint: disable=not-callable
    ),
    UniqueConstraint("user_id", "role_id", "tenant_id", name="uq_user_role_tenant"),
)
