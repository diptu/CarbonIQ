"""Association table linking roles and user for user_service"""

from __future__ import annotations

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import engine
from app.models.base import Base, BaseModel


class UserRole(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Association table linking users and roles.

    A user can have multiple roles, and each role can be assigned to multiple users.

    Attributes
    ----------
    id : UUID
        Unique identifier for the user-role association, automatically generated using UUID4.
    user_id : UUID
        Foreign key referencing the user's id. Cascades on delete.
    role_id : UUID
        Foreign key referencing the role's id. Cascades on delete.
    user : User
        Relationship to the User object.
    role : Role
        Relationship to the Role object.
    """

    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    # Foreign key to users table
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID of the user linked to this role",
    )

    # Foreign key to roles table
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID of the role assigned to the user",
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="roles",
    )

    role = relationship(
        "Role",
        back_populates="users",
    )

    def __repr__(self) -> str:
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


# Create table(s) in the database
Base.metadata.create_all(bind=engine)
