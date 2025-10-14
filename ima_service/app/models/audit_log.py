"""AuditLog model for tracking sensitive actions in the IMA service."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .user import User


class AuditLog(BaseModel):
    """
    Tracks sensitive actions performed by users for audit and compliance.

    Inherits all common fields (created_at, updated_at, tenant_id, created_by, updated_by)
    from BaseModel.
    """

    __tablename__ = "audit_logs"  # 🔑 Added explicit tablename

    # Audit Logs should NEVER be soft-deleted. The methods are removed below.
    # The BaseModel's deleted_at column should be unused or configured to NOT inherit.

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # 🔑 FIX: Foreign Key should be ON DELETE SET NULL
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    tenant_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    method: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    endpoint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)

    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # fields for traceability
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)

    # flexible JSON metadata
    extra: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # The inherited created_by/updated_by fields are redundant here, as the log
    # tracks the acting user in user_id, but their presence is harmless.

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", backref="audit_logs", lazy="joined")

    # Indexes for faster querying
    __table_args__ = (
        Index("ix_auditlog_user_id", "user_id"),
        Index("ix_auditlog_tenant_path", "tenant_path"),
        Index("ix_auditlog_action", "action"),
    )

    # ==============================
    # Helper Methods
    # ==============================

    # 🔑 FIX: REMOVED soft_delete and active methods.
    # Audit logs MUST NOT be soft-deleted. If the BaseModel adds these methods,
    # they must be overridden to raise an exception, or simply not used.

    def __repr__(self) -> str:
        return (
            f"<AuditLog user={self.user_id} action={self.action} "
            f"resource={self.resource} ip={self.ip_address}>"
        )
