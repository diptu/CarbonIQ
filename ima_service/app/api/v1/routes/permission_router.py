# app/api/v1/routes/permission_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.dependencies.auth import require_permissions, get_current_user
from app.models.user import User
from app.schemas.permission import (
    PermissionCreate,
    PermissionRead,
    PermissionListResponse,
)
from app.services.permission_service import PermissionService
from app.db.session import get_db as get_db_session
from sqlalchemy.orm import Session

router = APIRouter()


# -------------------------
# Create Permission
# -------------------------
@router.post(
    "/",
    response_model=PermissionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(["manage_permissions"]))],
)
async def create_permission(
    permission_in: PermissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """
    Create a new permission.
    Requires `manage_permissions` permission.
    """
    service = PermissionService(db)
    permission = service.create_permission(permission_in)
    return permission


# -------------------------
# List Permissions (Paginated)
# -------------------------
@router.get(
    "/",
    response_model=PermissionListResponse,
    dependencies=[Depends(require_permissions(["view_permissions"]))],
)
async def list_permissions(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """
    List all permissions (paginated).
    Requires `view_permissions` permission.
    """
    service = PermissionService(db)
    total, items = service.list_permissions(skip=skip, limit=limit)
    return {"total": total, "items": items}


# -------------------------
# Get Permission by ID
# -------------------------
@router.get(
    "/{permission_id}",
    response_model=PermissionRead,
    dependencies=[Depends(require_permissions(["view_permissions"]))],
)
async def get_permission(
    permission_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """
    Get a permission by ID.
    Requires `view_permissions` permission.
    """
    service = PermissionService(db)
    permission = service.get_permission(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission


# -------------------------
# Delete Permission
# -------------------------
@router.delete(
    "/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permissions(["manage_permissions"]))],
)
async def delete_permission(
    permission_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
):
    """
    Delete a permission by ID.
    Requires `manage_permissions` permission.
    """
    service = PermissionService(db)
    success = service.delete_permission(permission_id)
    if not success:
        raise HTTPException(status_code=404, detail="Permission not found")
    return None
