# app/services/permission_service.py
"""Tenant-scoped Permission service."""

from __future__ import annotations
from typing import Optional, List, Type

from .crud_service import CRUDService
from ..models.permission import Permission  # ORM model


class PermissionService(CRUDService[Permission]):
    """
    Tenant-aware Permission service.

    Inherits:
        - Tenant-scoped CRUD operations (list, get_by_id, create, update, soft_delete)
        - Transactional support
        - Audit logging
        - Query scoping via tenant_id
    """

    async def list_permissions(self, limit: int = 100, offset: int = 0) -> List[Permission]:
        """List all permissions within tenant context with pagination."""
        return await self.list(Permission, limit=limit, offset=offset)

    async def get_permission_by_id(self, permission_id: str) -> Optional[Permission]:
        """Get a permission by primary key within tenant context."""
        return await self.get_by_id(Permission, permission_id)
