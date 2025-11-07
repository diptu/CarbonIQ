# user_service/app/models/role_permission.py
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from user_service.app.models.base import BaseModel


class RolePermission(BaseModel):
    __tablename__ = "role_permissions"

    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)

    role_id = Column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)
    permission_id = Column(
        ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # association relationships
    role = relationship("Role")  # no back_populates!
    permission = relationship("Permission", back_populates="role_permissions")

    def __repr__(self):
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
