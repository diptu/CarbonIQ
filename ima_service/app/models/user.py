"""User model for multi-tenant RBAC system."""

import uuid
from typing import TYPE_CHECKING, Optional

import bcrypt
from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .role import Role


# --- Password hashing & verification --------------------------------


def hash_password(plain_password: str) -> str:
    """Hash plain password using bcrypt.

    Args
    ----
    plain_password : str
        Raw password to hash.

    Returns
    -------
    str
        Hashed password.
    """
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against hashed password.

    Args
    ----
    plain_password : str
        Raw password.
    hashed_password : str
        Hashed password stored in DB.

    Returns
    -------
    bool
        True if password matches, False otherwise.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


class User(BaseModel):
    """Represents an authenticated individual tied to a tenant."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("tenants.id"), nullable=True
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary="user_roles", back_populates="users"
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    # --- Security Methods (Domain Logic) ---
    @hybrid_property
    def password(self) -> str:
        """Prevent direct reading of the password hash."""
        raise AttributeError("Password is not readable")

    @password.setter  # type: ignore[no-redef]
    def password(self, password: str) -> None:
        """Hashes the password and updates the security stamp."""
        self._password_hash = hash_password(password)
        self.security_stamp = uuid.uuid4()  # Invalidate old tokens

    def verify_password(self, password: str) -> bool:
        """Verifies a plaintext password against the stored hash."""
        return verify_password(password, self.password_hash)

    def activate(self) -> None:
        """Activate the user."""
        self.is_active = True
        self.touch()

    def deactivate(self) -> None:
        """Deactivate the user."""
        self.is_active = False
        self.touch()
