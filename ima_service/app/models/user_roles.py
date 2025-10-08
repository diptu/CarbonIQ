# app/models/user_roles.py
import uuid
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base_class import Base, TimestampMixin
from .user import User
from .role import Role
from .tenant import Tenant


class UserRole(Base, TimestampMixin):
    __tablename__ = "user_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), nullable=False
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False
    )

    # Relationships
    user: Mapped[User] = relationship("User", back_populates="roles", lazy="selectin")
    role: Mapped[Role] = relationship("Role", lazy="selectin")
    tenant: Mapped[Tenant] = relationship(
        "Tenant", back_populates="user_roles", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", "tenant_id", name="uix_user_role"),
    )

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"
