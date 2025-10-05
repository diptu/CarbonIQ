from sqlalchemy import Column, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.base_class import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), primary_key=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "tenant_id", name="uq_user_role_tenant"),
    )

    user = relationship("User", back_populates="roles_association")
    role = relationship("Role", back_populates="users_association")
