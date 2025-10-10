"""User model definition.

Represents application users linked to a tenant, with role-based
access control (RBAC) relationships.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (
    String,
    Boolean,
    Enum as SQLEnum,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_class import Base


class GenderEnum(str, Enum):
    """
    Gender enumeration.

    Notes
    -----
    Defines the allowed gender values for a user record.
    """

    MALE = "Male"
    FEMALE = "Female"
    OTHER = "Other"


class User(Base):
    """
    User.

    Notes
    -----
    Represents an application user within a tenant. Users can have
    multiple roles assigned through the `user_roles` association table.
    Superusers bypass RBAC restrictions.

    Attributes
    ----------
    id : uuid.UUID
        Primary key.
    email : str
        Unique email address used for login.
    password_hash : str
        Hashed password value.
    first_name : Optional[str]
        User's given name.
    last_name : Optional[str]
        User's family name.
    gender : Optional[GenderEnum]
        Gender identifier (Male, Female, or Other).
    country : Optional[str]
        ISO country code or country name.
    is_active : bool
        True if the account is active.
    is_superuser : bool
        True if the user has unrestricted administrative access.
    tenant_id : uuid.UUID
        Foreign key referencing `tenants.id`.
    tenant : Tenant
        Relationship to the associated tenant.
    roles : list[Role]
        Roles assigned to the user through the `user_roles` table.
    created_at : datetime
        Timestamp when created (from Base).
    updated_at : datetime
        Timestamp when last updated (from Base).
    """

    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", "tenant_id", name="uq_users_email_tenant"),
        CheckConstraint("position('@' in email) > 1", name="ck_users_email_valid"),
    )
    # pylint: disable=too-few-public-methods

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Primary key identifier (UUID).",
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=False,  # unique enforced via UniqueConstraint with tenant
        index=True,
        doc="Unique email address for login.",
    )

    password_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Hashed password value.",
    )

    first_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="User's first name (optional).",
    )

    last_name: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="User's last name (optional).",
    )

    gender: Mapped[Optional[GenderEnum]] = mapped_column(
        SQLEnum(GenderEnum, name="gender_enum", native_enum=False),
        nullable=True,
        doc="User's gender: Male, Female, or Other (optional).",
    )

    country: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        doc="Country name or ISO country code (optional).",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
        doc="Indicates whether the user account is active.",
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
        doc="True if the user has unrestricted administrative access.",
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        doc="Foreign key linking to the owning tenant.",
    )

    tenant: Mapped["Tenant"] = relationship(
        "Tenant",
        back_populates="users",
        doc="Relationship to the associated tenant.",
    )

    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary="user_roles",
        back_populates="users",
        doc="Roles assigned to the user through the user_roles table.",
    )
    permissions: Mapped[list["UserPermission"]] = relationship(
        "UserPermission", back_populates="user", cascade="all, delete-orphan"
    )

    # --- Convenience methods ---

    def __repr__(self) -> str:
        """Return a concise string representation."""
        return f"<User {self.email} (id={self.id})>"

    @property
    def display_name(self) -> str:
        """Return full name or fallback to email prefix."""
        name = self.full_name()
        return name or self.email.split("@")[0]

    def full_name(self) -> str:
        """
        Return the user's full name.

        Returns
        -------
        str
            Concatenated first and last name if available, or 'Unknown' if missing.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name or self.last_name:
            return self.first_name or self.last_name
        return "Unknown"

    def normalize_email(self) -> None:
        """
        Normalize email address in-place.

        Converts domain part to lowercase for consistent lookups.
        """
        if self.email:
            self.email = self.email.strip()
            local, _, domain = self.email.partition("@")
            self.email = f"{local}@{domain.lower()}"

    def has_role(self, role_name: str) -> bool:
        """
        Check whether the user has a role by name.

        Parameters
        ----------
        role_name : str
            The name of the role to check.

        Returns
        -------
        bool
            True if the role is assigned.
        """
        return any(role.name == role_name for role in self.roles)

    def to_dict(self) -> dict[str, object]:
        """
        Convert user instance to a serializable dictionary.

        Returns
        -------
        dict of str to object
            Dictionary containing basic user information.
        """
        return {
            "id": str(self.id),
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "gender": self.gender.value if self.gender else None,
            "country": self.country,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "tenant_id": str(self.tenant_id),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
