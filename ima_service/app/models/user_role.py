"""UserRole association table."""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class UserRole(BaseModel):
    """Many-to-many relationship: User <-> Role."""

    user_id: Mapped = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped = mapped_column(ForeignKey("roles.id"), primary_key=True)

    def __repr__(self) -> str:  # <-- Added method to resolve R0903
        return f"<UserRole user={self.user_id} role={self.role_id}>"
