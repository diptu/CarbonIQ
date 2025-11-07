"""API routes for managing RolePermission assignments using build_api_response formatting."""

import time
from functools import wraps
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from shared_service.app.core.deps import get_cached_current_user, require_permissions
from shared_service.app.utils.response import APIResponse, build_api_response
from sqlalchemy.orm import Session

from user_service.app.crud.role_permission import role_permission_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.role_permission import RolePermissionCreate, RolePermissionRead

router = APIRouter(prefix="/role-permissions", tags=["role_permissions"])


# ---------------------------------------------------
# Utility: Add request duration (ms) to response.meta
# ---------------------------------------------------
def request_timer(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        response = await func(*args, **kwargs)
        duration = round((time.perf_counter() - start) * 1000, 2)

        if isinstance(response, dict):
            response.setdefault("meta", {})
            response["meta"]["request_duration_ms"] = duration
            return response

        if hasattr(response, "meta"):
            response.meta.request_duration_ms = duration

        return response

    return wrapper


# ---------------------
# Reusable fetch
# ---------------------
def fetch_role_permission_or_404(role_permission_id: UUID, db: Session):
    rp = role_permission_crud.get(db, role_permission_id)
    if not rp:
        raise HTTPException(status_code=404, detail="Role-Permission assignment not found")
    return rp


# ---------------------
# Create RolePermission
# ---------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(permissions=["role_permission.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def create_role_permission(
    rp_in: RolePermissionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    rp = role_permission_crud.create(db, rp_in)
    return build_api_response(
        request, current_user, RolePermissionRead.model_validate(rp)
    ).model_dump()


# ---------------------
# Get Single RolePermission
# ---------------------
@router.get(
    "/{role_permission_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["role_permission.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def get_role_permission(
    role_permission_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    rp = fetch_role_permission_or_404(role_permission_id, db)
    return build_api_response(
        request, current_user, RolePermissionRead.model_validate(rp)
    ).model_dump()


# ---------------------
# List RolePermissions
# ---------------------
@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["role_permission.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def list_role_permissions(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    total = role_permission_crud.count(db)
    rps = role_permission_crud.get_all(db, skip=skip, limit=limit)
    rps_data = [RolePermissionRead.model_validate(rp) for rp in rps]

    result = {
        "role_permissions": rps_data,
        "count": total,
        "perPage": limit,
        "previousPage": skip - limit if skip - limit >= 0 else None,
        "nextPage": skip + limit if skip + limit < total else None,
    }

    return build_api_response(request, current_user, result).model_dump()


# ---------------------
# Delete RolePermission
# ---------------------
@router.delete(
    "/{role_permission_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["role_permission.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def delete_role_permission(
    role_permission_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    fetch_role_permission_or_404(role_permission_id, db)
    deleted_rp = role_permission_crud.delete(db, role_permission_id)
    return build_api_response(
        request, current_user, RolePermissionRead.model_validate(deleted_rp)
    ).model_dump()
