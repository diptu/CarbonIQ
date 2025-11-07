# user_service/app/models/user_role.py
from __future__ import annotations

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from user_service.app.models.base import BaseModel


class UserRole(BaseModel):
    __tablename__ = "user_roles"

    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role_id = Column(ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"
