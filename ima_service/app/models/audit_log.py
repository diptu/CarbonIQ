"""Audit log for tracking sensitive actions."""  # <-- Added module docstring

import uuid
from datetime import datetime

from sqlalchemy import (DateTime, ForeignKey,  # <-- ADDED DateTime and func
                        Integer, String, func)
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class AuditLog(BaseModel):
    """Tracks sensitive actions performed by users."""

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id"), nullable=True
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=E1102
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.user_id} {self.action} {self.resource}>"
