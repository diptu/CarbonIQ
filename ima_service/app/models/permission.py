import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.base_class import Base, TimestampMixin


class Permission(Base, TimestampMixin):
    __tablename__ = "permissions"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)

    role_permissions = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    roles = relationship(
        "Role",
        secondary="role_permissions",
        viewonly=True,
        back_populates="permissions",
        lazy="selectin",
    )
