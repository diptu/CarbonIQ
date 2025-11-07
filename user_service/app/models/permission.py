# user_service/app/models/permission.py
from __future__ import annotations

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from user_service.app.models.base import BaseModel


class Permission(BaseModel):
    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # association table link
    role_permissions = relationship(
        "RolePermission", back_populates="permission", cascade="all, delete-orphan"
    )

    # many-to-many to Role
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="selectin",
        viewonly=True,
    )

    def __repr__(self):
        return f"<Permission(name={self.name!r})>"
