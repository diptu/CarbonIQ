"""User model definition for the user_service."""

from __future__ import annotations

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.db.session import engine
from app.models.base import Base, BaseModel


class User(BaseModel):  # pylint: disable=too-few-public-methods
    """
    Core user model representing system users across tenants.

    Attributes
    ----------
    id : UUID
        Unique identifier for the user, automatically generated using UUID4.
    email : str
        User's email address, must be unique and not nullable.
    hashed_password : str
        User's hashed password for authentication.
    full_name : str | None
        Optional full name of the user.
    is_active : bool
        Indicates whether the user account is active.
    is_verified : bool
        Indicates whether the user's email has been verified.
    is_superuser : bool
        Indicates whether the user has superuser privileges.
    roles : list[UserRole]
        Relationship linking the user to their assigned roles.
        Cascade deletes so related UserRole entries are removed when a User is deleted.
    permissions : list[UserPermission]
        Relationship linking the user to directly assigned permissions.
        Cascade deletes so related UserPermission entries are removed when a User is deleted.
    """

    __tablename__ = "users"

    # Email of the user
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User's unique email address for login",
    )

    # Hashed password
    hashed_password = Column(
        String(255), nullable=False, comment="Hashed password for user authentication"
    )

    # Optional full name
    full_name = Column(String(255), nullable=True, comment="Optional full name of the user")

    # Active status
    is_active = Column(Boolean, default=True, comment="Indicates if the user account is active")

    # Email verification status
    is_verified = Column(
        Boolean, default=False, comment="Indicates if the user's email has been verified"
    )

    # Superuser flag
    is_superuser = Column(
        Boolean, default=False, comment="Indicates if the user has superuser privileges"
    )
    # single association
    assignments = relationship(
        "UserRolePermission",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(email={self.email!r}, active={self.is_active})>"


# Create table(s) in the database
Base.metadata.create_all(bind=engine)
