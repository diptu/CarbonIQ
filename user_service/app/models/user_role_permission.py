"""UserRolePermission association table"""

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import engine
from app.models.base import BaseModel

from .base import Base, BaseModel


class UserRolePermission(BaseModel):
    __tablename__ = "user_role_permissions"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "permission_id", name="uq_user_role_permission"),
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=True,  # ✅ nullable → direct user permission possible
    )

    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # relationships
    user = relationship("User", back_populates="assignments")
    role = relationship("Role", back_populates="assignments")
    permission = relationship("Permission", back_populates="assignments")

    def __repr__(self):
        return (
            f"<UserRolePermission(user={self.user_id}, "
            f"role={self.role_id}, permission={self.permission_id})>"
        )


# Create table(s) in the database
Base.metadata.create_all(bind=engine)
