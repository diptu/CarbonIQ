"""UserPermission Association table linking users and permissions for the user_service."""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import engine

from .base import Base, BaseModel


class UserPermission(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Association table linking users and permissions.

    A user can have multiple direct permissions,
    and each permission can be assigned to multiple users.

    Attributes
    ----------
    id : UUID
        Unique identifier for the user-permission association, automatically generated using UUID4.
    user_id : UUID
        Foreign key referencing the user's id. Cascades on delete.
    permission_id : UUID
        Foreign key referencing the permission's id. Cascades on delete.
    user : User
        Relationship to the User object.
    permission : Permission
        Relationship to the Permission object.
    """

    __tablename__ = "user_permissions"

    # Foreign key to users table
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID of the user assigned this permission",
    )

    # Foreign key to permissions table
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID of the permission assigned to the user",
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="user_permissions",
    )

    permission = relationship(
        "Permission",
        back_populates="user_permissions",
    )

    def __repr__(self) -> str:
        return f"<UserPermission(user_id={self.user_id}, permission_id={self.permission_id})>"


# Create table(s) in the database
Base.metadata.create_all(bind=engine)
