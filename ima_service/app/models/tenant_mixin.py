"""TenantMixin for multi-tenant models.

Provides tenant-aware query filtering for ORM models in IMA service.
"""

from typing import Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy.orm import Query, Session
from sqlalchemy import cast
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

T = TypeVar("T", bound="TenantMixin")


class TenantMixin:  # pylint:disable=R0903
    """Mixin to provide tenant-aware filtering for ORM models."""

    tenant_id: Optional[UUID]

    @classmethod
    def for_tenant(cls: Type[T], session: Session, tenant_id: str) -> Query:
        """Return SQLAlchemy Query filtered by tenant_id."""
        try:
            tenant_uuid: UUID = UUID(tenant_id)
        except ValueError:
            tenant_uuid = UUID(int=0)

        return session.query(cls).filter(cast(cls.tenant_id, PG_UUID) == tenant_uuid)
