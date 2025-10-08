# app/models/role_permissions.py
import uuid
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base_class import Base, TimestampMixin
from .role import Role
from .permission import Permission


class RolePermission(Base, TimestampMixin):
    __tablename__ = "role_permissions"

    id: Mapped[uuid.UUID] = mapped_column(
        uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    role: Mapped[Role] = relationship("Role", lazy="selectin")
    permission: Mapped[Permission] = relationship("Permission", lazy="selectin")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uix_role_permission"),
    )

    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
