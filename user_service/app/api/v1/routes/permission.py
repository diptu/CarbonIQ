"""API routes for managing permissions using build_api_response formatting with AsyncSession."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from shared_service.app.core.deps import get_cached_current_user, require_permissions
from shared_service.app.utils.fetch import fetch_or_404
from shared_service.app.utils.paggination import paginate
from shared_service.app.utils.response import APIResponse, build_api_response
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.app.api.v1.routes.docs.permission import (
    CREATE_PERMISSION_DOCS,
    DELETE_PERMISSION_DOCS,
    GET_PERMISSION_DOCS,
    LIST_PERMISSIONS_DOCS,
    UPDATE_PERMISSION_DOCS,
)
from user_service.app.core.config import settings
from user_service.app.crud.permission import permission_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.permission import PermissionCreate, PermissionOut, PermissionUpdate

router = APIRouter(prefix="/permissions", tags=["permissions"])


# ---------------------
# Dependency: Fetch permission or 404
# ---------------------
async def fetch_permission_or_404(permission_id: UUID, db: AsyncSession = Depends(get_db)):
    return await fetch_or_404(permission_crud.get, db, permission_id)


# ---------------------
# Create Permission
# ---------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(["permission.create"]))],
    openapi_extra={**CREATE_PERMISSION_DOCS, "security": [{"BearerAuth": []}]},
)
async def create_permission(
    permission_in: PermissionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    existing = await permission_crud.get_by_name(db, permission_in.name)
    if existing:
        raise HTTPException(status_code=409, detail="Permission already exists")

    perm = await permission_crud.create(db, permission_in)
    return build_api_response(request, current_user, PermissionOut.model_validate(perm))


# ---------------------
# Get Single Permission
# ---------------------
@router.get(
    "/{permission_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["permission.read"]))],
    openapi_extra={**GET_PERMISSION_DOCS, "security": [{"BearerAuth": []}]},
)
async def get_permission(
    permission_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    perm = await fetch_permission_or_404(permission_id, db)
    return build_api_response(request, current_user, PermissionOut.model_validate(perm))


# ---------------------
# List Permissions
# ---------------------
@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["permission.read"]))],
    openapi_extra={**LIST_PERMISSIONS_DOCS, "security": [{"BearerAuth": []}]},
)
async def list_permissions(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    total = await permission_crud.count(db)
    perms = await permission_crud.get_all(db, skip=skip, limit=limit) or []
    perms_data = [PermissionOut.model_validate(p) for p in perms]
    pagination = paginate(skip=skip, limit=limit, total=total)

    result = {"permissions": perms_data, **pagination}
    return build_api_response(request, current_user, result, status_code=status.HTTP_200_OK)


# ---------------------
# Update Permission
# ---------------------
@router.put(
    "/{permission_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["permission.update"]))],
    openapi_extra={**UPDATE_PERMISSION_DOCS, "security": [{"BearerAuth": []}]},
)
async def update_permission(
    permission_id: UUID,
    permission_in: PermissionUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    perm = await fetch_permission_or_404(permission_id, db)

    # Check for duplicate name
    if permission_in.name:
        existing = await permission_crud.get_by_name(db, permission_in.name)
        if existing and existing.id != permission_id:
            raise HTTPException(
                status_code=409,
                detail=f"Permission with name '{permission_in.name}' already exists",
            )

    updated = await permission_crud.update(db, perm, permission_in)
    return build_api_response(request, current_user, PermissionOut.model_validate(updated))


# ---------------------
# Delete Permission
# ---------------------
@router.delete(
    "/{permission_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["permission.delete"]))],
    openapi_extra={**DELETE_PERMISSION_DOCS, "security": [{"BearerAuth": []}]},
)
async def delete_permission(
    permission_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    perm = await fetch_permission_or_404(permission_id, db)
    await permission_crud.delete(db, permission_id)

    return build_api_response(
        request,
        current_user,
        result={"message": f"Permission {permission_id} deleted successfully"},
        status_code=status.HTTP_200_OK,
    )
