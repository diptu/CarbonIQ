"""API routes for managing RolePermission assignments using build_api_response formatting."""

import time
from functools import wraps
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from shared_service.app.core.deps import get_cached_current_user, require_permissions
from shared_service.app.utils.response import build_api_response
from sqlalchemy.orm import Session

from user_service.app.crud.role_permission import role_permission_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.role_permission import RolePermissionCreate

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
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(["role_permission.create"]))],
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

    payload = {
        "id": str(rp.id),
        "role_id": str(rp.role_id),
        "permission_id": str(rp.permission_id),
    }

    return build_api_response(
        request=request,
        current_user=current_user,
        result=payload,
        success=True,
        message="Role-Permission assigned successfully",
        include_user_context=False,
    ).model_dump()


# ---------------------
# Get Single RolePermission
# ---------------------
@router.get(
    "/{role_permission_id}",
    dependencies=[Depends(require_permissions(["role_permission.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def get_role_permission(
    role_permission_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    rp = fetch_role_permission_or_404(role_permission_id, db)

    payload = {
        "id": str(rp.id),
        "role_id": str(rp.role_id),
        "permission_id": str(rp.permission_id),
    }

    return build_api_response(
        request=request,
        current_user=current_user,
        result=payload,
        include_user_context=False,
    ).model_dump()


# ---------------------
# List RolePermissions
# ---------------------
@router.get(
    "/",
    dependencies=[Depends(require_permissions(["role_permission.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def list_role_permissions(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    total = role_permission_crud.count(db)
    rps = role_permission_crud.get_all(db, skip=skip, limit=limit)

    rps_data = [
        {"id": str(rp.id), "role_id": str(rp.role_id), "permission_id": str(rp.permission_id)}
        for rp in rps
    ]

    current_page = (skip // limit) + 1
    total_pages = (total + limit - 1) // limit

    result = {
        "role_permissions": rps_data,
        "count": total,
        "perPage": limit,
        "previousPage": current_page - 1 if current_page > 1 else None,
        "nextPage": current_page + 1 if current_page < total_pages else None,
    }

    return build_api_response(
        request=request,
        current_user=current_user,
        result=result,
        include_user_context=False,
    ).model_dump()


# ---------------------
# Delete RolePermission
# ---------------------
@router.delete(
    "/{role_permission_id}",
    dependencies=[Depends(require_permissions(["role_permission.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def delete_role_permission(
    role_permission_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    fetch_role_permission_or_404(role_permission_id, db)
    deleted_rp = role_permission_crud.delete(db, role_permission_id)

    payload = {
        "id": str(deleted_rp.id),
        "role_id": str(deleted_rp.role_id),
        "permission_id": str(deleted_rp.permission_id),
    }

    return build_api_response(
        request=request,
        current_user=current_user,
        result=payload,
        include_user_context=False,
        success=True,
        message="Role-Permission deleted successfully",
    ).model_dump()
