import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.base_class import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)

    roles_association = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )
    roles = relationship(
        "Role",
        secondary="user_roles",
        viewonly=True,
        back_populates="users",
        lazy="selectin",
    )
