"""Tenant model definition.

Represents tenants in a multi-tenant system, supporting hierarchical
RBAC. Activation status is independent per tenant.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import String, Boolean, ForeignKey, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_class import Base
from .user import User


class Tenant(Base):
    """
    Tenant.

    Notes
    -----
    Represents a tenant in a multi-tenant system. Supports hierarchical
    relationships via `parent_id` and can contain multiple users. Each
    tenant's `is_active` is independent of parent or children.
    """

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Primary key identifier (UUID).",
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        doc="Human-readable tenant name, unique.",
    )

    domain: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        doc="Tenant's domain, unique.",
    )

    schema_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        doc="Database schema name for the tenant, unique.",
    )

    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
        doc="Parent tenant reference for hierarchy.",
    )

    parent: Mapped[Optional["Tenant"]] = relationship(
        "Tenant",
        remote_side=[id],
        backref="sub_tenants",
        doc="Relationship to the parent tenant.",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
        doc="Indicates whether the tenant is active.",
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="tenant",
        doc="List of users belonging to this tenant.",
    )

    # --- Hierarchy / Convenience methods ---

    def get_hierarchy_path(self) -> List[str]:
        """Return the full hierarchy path of tenant names from root."""
        path = []
        current: Optional[Tenant] = self
        while current:
            path.insert(0, current.name)
            current = current.parent
        return path

    def get_all_descendants(self) -> List[Tenant]:
        """Recursively retrieve all child and grandchild tenants."""
        descendants: List[Tenant] = []

        def _collect_children(tenant: Tenant) -> None:
            for child in tenant.sub_tenants:
                descendants.append(child)
                _collect_children(child)

        _collect_children(self)
        return descendants

    @property
    def level(self) -> int:
        """Return the depth level of this tenant in the hierarchy."""
        lvl = 0
        current = self.parent
        while current:
            lvl += 1
            current = current.parent
        return lvl

    def to_tree(self) -> dict:
        """Return tenant and all descendants as a nested dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "is_active": self.is_active,
            "sub_tenants": [child.to_tree() for child in self.sub_tenants],
        }

    def __repr__(self) -> str:
        """Return a concise string representation."""
        return f"<Tenant {self.name} (id={self.id})>"


# --- Validation hooks ---


@event.listens_for(Tenant, "before_insert")
@event.listens_for(Tenant, "before_update")
def prevent_cycles(mapper, connection, target: Tenant) -> None:
    """Prevent circular parent-child relationships."""
    current = target.parent
    while current:
        if current.id == target.id:
            raise ValueError("Tenant cannot be its own ancestor.")
        current = current.parent
