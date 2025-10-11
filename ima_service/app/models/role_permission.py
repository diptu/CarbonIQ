"""RolePermission association table."""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class RolePermission(BaseModel):
    """Many-to-many relationship: Role <-> Permission."""

    role_id: Mapped = mapped_column(ForeignKey("roles.id"), primary_key=True)
    permission_id: Mapped = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )

    def __repr__(self) -> str:  # <-- Added method to resolve R0903
        return f"<RolePermission role={self.role_id} permission={self.permission_id}>"
