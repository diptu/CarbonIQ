# app/models/role.py
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base_class import Base
import uuid


class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255))
    is_system = Column(Boolean, default=False)

    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
    )
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles",
    )
