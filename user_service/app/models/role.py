"""Role model definition for the user_service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import engine

from .base import Base, BaseModel

if TYPE_CHECKING:
    from app.models.user_permission import UserPermission
    from app.models.user_role import UserRole


class Role(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Role model representing a system or tenant-specific role.

    Attributes
    ----------
    id : UUID
        Unique identifier for the role, automatically generated using UUID4.
    name : str
        Name of the role (e.g., 'admin', 'editor', 'viewer').
        Must be unique and not nullable.
    description : str | None
        Optional textual description of the role’s purpose.
    users : list[UserRole]
        Relationship to UserRole linking users assigned to this role.
        Cascade deletes so related UserRole entries are removed when a Role is deleted.
    permissions : list[UserPermission]
        Relationship to UserPermission linking permissions assigned to this role.
        Cascade deletes so related UserPermission entries are removed when a Role is deleted.
    """

    __tablename__ = "roles"

    # Name of the role
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="Role name, must be unique (e.g., 'admin', 'editor')",
    )

    # Optional description of the role
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Optional description explaining the purpose of the role"
    )

    # Relationships
    users: Mapped[list["UserRole"]] = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    permissions: Mapped[list["UserPermission"]] = relationship(
        "UserPermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Role(name={self.name})>"


# Create table(s) in the database
Base.metadata.create_all(bind=engine)
