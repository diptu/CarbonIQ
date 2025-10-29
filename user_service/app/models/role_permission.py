"""Association table linking roles and permissions for user_service"""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import engine
from app.models.base import Base, BaseModel


class RolePermission(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Association table linking roles and permissions.

    Each record grants a specific permission to a role.

    Attributes
    ----------
    id : UUID
        Unique identifier for the role-permission association,
        automatically generated using UUID4.
    role_id : UUID
        Foreign key referencing the role's id. Cascades on delete.
    permission_id : UUID
        Foreign key referencing the permission's id. Cascades on delete.
    role : Role
        Relationship to the Role object.
    permission : Permission
        Relationship to the Permission object.
    """

    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)

    # Foreign key to roles table
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID of the role assigned this permission",
    )

    # Foreign key to permissions table
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID of the permission granted to the role",
    )

    # Relationships
    role = relationship(
        "Role", back_populates="permissions", comment="Role object linked to this association"
    )

    permission = relationship(
        "Permission", back_populates="roles", comment="Permission object linked to this association"
    )

    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"


# Create table(s) in the database
Base.metadata.create_all(bind=engine)
