# ima_service/app/models/permission.py (Example structure)

"""Permission model for the RBAC system."""  # <-- Good practice docstring

import uuid
from typing import TYPE_CHECKING, Optional  # <-- Add TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

# --- SOLUTION: Import for Type Checking Only ---
# This resolves the forward reference "Role" for mypy without
# causing a runtime circular import.
if TYPE_CHECKING:
    from .role import Role
# -----------------------------------------------


class Permission(BaseModel):
    """Defines a specific action or resource access right."""

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Line 20 (or similar) - The source of the error:
    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary="role_permissions", back_populates="permissions"
    )

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"
