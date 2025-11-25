"""API routes for managing RolePermission assignments using build_api_response formatting."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from shared_service.app.core.deps import get_cached_current_user, require_permissions
from shared_service.app.utils.fetch import fetch_or_404
from shared_service.app.utils.paggination import paginate
from shared_service.app.utils.response import APIResponse, build_api_response
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.app.core.config import settings
from user_service.app.crud.role_permission import role_permission_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.role_permission import RolePermissionCreate, RolePermissionRead

router = APIRouter(prefix="/role-permissions", tags=["role_permissions"])


# ---------------------
# Dependency: Fetch role_permission or 404
# ---------------------
async def fetch_role_permission_or_404(
    role_permission_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> RolePermissionRead:
    return await fetch_or_404(role_permission_crud.get, db, role_permission_id)


# ---------------------
# Create RolePermission
# ---------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(["role_permission.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def create_role_permission(
    rp_in: RolePermissionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    # Prevent duplicate assignment
    existing = await role_permission_crud.get_by_role_permission(
        db, rp_in.role_id, rp_in.permission_id
    )
    if existing:
        raise HTTPException(status_code=409, detail="RolePermission assignment already exists")

    rp = await role_permission_crud.create(db, rp_in)
    payload = RolePermissionRead.model_validate(rp)

    return build_api_response(
        request=request,
        current_user=current_user,
        result=payload.model_dump(),
        status_code=status.HTTP_201_CREATED,
    )


# ---------------------
# Get Single RolePermission
# ---------------------
@router.get(
    "/{role_permission_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role_permission.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def get_role_permission(
    role_permission_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    rp = await fetch_role_permission_or_404(role_permission_id, db)
    payload = RolePermissionRead.model_validate(rp)

    return build_api_response(
        request=request,
        current_user=current_user,
        result=payload.model_dump(),
        status_code=status.HTTP_200_OK,
    )


# ---------------------
# List RolePermissions
# ---------------------
@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role_permission.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def list_role_permissions(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    total = await role_permission_crud.count(db)
    rps = await role_permission_crud.get_all(db, skip=skip, limit=limit) or []

    rps_data = [RolePermissionRead.model_validate(rp) for rp in rps]
    pagination = paginate(skip=skip, limit=limit, total=total)

    result = {"role_permissions": rps_data, **pagination}

    return build_api_response(
        request=request,
        current_user=current_user,
        result=result,
        status_code=status.HTTP_200_OK,
    )


# ---------------------
# Delete RolePermission
# ---------------------
@router.delete(
    "/{role_permission_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role_permission.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def delete_role_permission(
    role_permission_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    rp = await fetch_role_permission_or_404(role_permission_id, db)
    await role_permission_crud.delete(db, role_permission_id)

    return build_api_response(
        request=request,
        current_user=current_user,
        result={"message": f"RolePermission {role_permission_id} deleted successfully"},
        status_code=status.HTTP_200_OK,
    )
