# app/models/permission.py
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base_class import Base
import uuid


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255))

    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
    )
