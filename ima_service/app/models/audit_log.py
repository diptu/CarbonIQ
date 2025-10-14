"""AuditLog model for tracking sensitive actions in the IMA service."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

if TYPE_CHECKING:
    from .user import User


class AuditLog(BaseModel):
    """
    Tracks sensitive actions performed by users for audit and compliance.

    Parameters
    ----------
    user_id : Optional[uuid.UUID]
        The ID of the user performing the action.
    tenant_id : Optional[uuid.UUID]
        Tenant context of the action.
    tenant_path : Optional[str]
        Hierarchical tenant path (e.g., "org/tenant/subtenant").
    action : str
        The action performed (e.g., 'CREATE', 'DELETE').
    resource : str
        Target resource affected by the action.
    method : Optional[str]
        HTTP method used for the action.
    endpoint : Optional[str]
        API endpoint accessed.
    status_code : int
        HTTP status code resulting from the action.
    ip_address : Optional[str]
        IP address of the request origin.
    device_info : Optional[str]
        Device or client information.
    correlation_id : Optional[str]
        Correlation ID for request tracing.
    trace_id : Optional[str]
        Trace ID for distributed tracing.
    extra : Optional[dict]
        Flexible JSON metadata.
    created_at : datetime
        Timestamp when the log entry was created.
    """

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    tenant_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource: Mapped[str] = mapped_column(String(100), nullable=False)
    method: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    endpoint: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)

    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    device_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # NEW fields for traceability
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)
    trace_id: Mapped[Optional[str]] = mapped_column(String(100), index=True, nullable=True)

    # NEW flexible JSON metadata
    extra: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

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

    def soft_delete(self):
        """Soft-delete the audit log entry without removing from DB."""
        self.deleted_at = datetime.utcnow()
        self.touch()

    @classmethod
    def active(cls, session):
        """Return query for audit logs that are not soft-deleted."""
        return session.query(cls).filter(cls.deleted_at.is_(None))

    def __repr__(self) -> str:
        return (
            f"<AuditLog user={self.user_id} action={self.action} "
            f"resource={self.resource} ip={self.ip_address}>"
        )
