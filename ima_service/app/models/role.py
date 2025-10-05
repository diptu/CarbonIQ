import uuid
from sqlalchemy import Boolean, Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.base_class import Base, TimestampMixin
from .user_roles import UserRole


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)  # NULL = system/global role
    name = Column(String, nullable=False)
    level = Column(Integer, nullable=False, default=1)
    description = Column(String, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)

    # Many-to-many with permissions
    role_permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        viewonly=True,
        back_populates="roles",
        lazy="selectin",
    )

    # Many-to-many with users via UserRole
    users_association = relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan", lazy="selectin"
    )
    users = relationship(
        "User",
        secondary="user_roles",
        viewonly=True,
        back_populates="roles",
        lazy="selectin",
    )
