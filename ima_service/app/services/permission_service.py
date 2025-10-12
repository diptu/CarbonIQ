"""Tenant-scoped Permission service."""

from __future__ import annotations

from .crud_service import CRUDService
from ..models.permission import Permission  # ORM model


class PermissionService(CRUDService[Permission]):
    """Tenant-aware Permission service."""

    # inherits all CRUD + RLS + auditing functionality
