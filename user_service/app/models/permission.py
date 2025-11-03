"""Permission model definition for the user_service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from user_service.app.db.session import engine

from .base import Base, BaseModel

if TYPE_CHECKING:
    pass


class Permission(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Represents an action or capability that can be assigned to a role or user.

    Attributes
    ----------
    id : UUID
        Unique identifier for the permission, automatically generated using UUID4.
    name : str
        Name of the permission (e.g., 'create_user', 'delete_tenant', 'view_reports').
        Must be unique and not nullable.
    description : str | None
        Optional textual description of what this permission allows.
    roles : list[RolePermission]
        Relationship to RolePermission linking roles assigned with this permission.
        Cascade deletes so related RolePermission entries are removed when a Permission is deleted.
    users : list[UserPermission]
        Relationship to UserPermission linking users assigned with this permission.
        Cascade deletes so related UserPermission entries are removed when a Permission is deleted.
    """

    __tablename__ = "permissions"

    # Name of the permission
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Permission name, must be unique (e.g., 'create_user', 'view_reports')",
    )

    # Optional description
    description = Column(
        Text, nullable=True, comment="Optional description explaining the purpose of the permission"
    )

    assignments = relationship(
        "UserRolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Permission(name={self.name!r})>"


# Create table(s) in the database
Base.metadata.create_all(bind=engine)
