"""API routes for managing permissions."""

import time
from functools import wraps
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from shared_service.app.core.deps import get_cached_current_user, require_permissions
from shared_service.app.utils.response import APIResponse, build_api_response
from sqlalchemy.orm import Session

from user_service.app.crud.permission import permission_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.permission import PermissionCreate, PermissionOut, PermissionUpdate

router = APIRouter(prefix="/permissions", tags=["permissions"])


# ---------------------------------------------------
# Utility: Add request duration (ms) to response.meta
# ---------------------------------------------------
def request_timer(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        response = await func(*args, **kwargs)
        duration = round((time.perf_counter() - start) * 1000, 2)

        # ✅ handle dict return
        if isinstance(response, dict):
            response.setdefault("meta", {})
            response["meta"]["request_duration_ms"] = duration
            return response

        # ✅ handle APIResponse model return
        if hasattr(response, "meta"):
            response.meta.request_duration_ms = duration

        return response

    return wrapper


# ---------------------
# Create Permission
# ---------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(["permission.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def create_permission(
    permission_in: PermissionCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    if permission_crud.get_by_name(db, permission_in.name):
        raise HTTPException(status_code=400, detail="Permission already exists")

    perm = permission_crud.create(db, permission_in)
    return build_api_response(
        request, current_user, PermissionOut.model_validate(perm)
    ).model_dump()


# ---------------------
# Get Permission
# ---------------------
@router.get(
    "/{permission_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["permission.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def get_permission(
    permission_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    perm = permission_crud.get(db, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    return build_api_response(
        request, current_user, PermissionOut.model_validate(perm)
    ).model_dump()


# ---------------------
# List Permissions
# ---------------------
@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["permission.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def list_permissions(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    total_permissions = permission_crud.count(db)
    perms = permission_crud.get_all(db, skip=skip, limit=limit)
    perms_data = [PermissionOut.model_validate(p) for p in perms]

    result = {
        "permissions": perms_data,
        "count": total_permissions,
        "perPage": limit,
        "previousPage": skip - limit if skip - limit >= 0 else None,
        "nextPage": skip + limit if skip + limit < total_permissions else None,
    }

    return build_api_response(request, current_user, result).model_dump()


# ---------------------
# Update Permission
# ---------------------
@router.put(
    "/{permission_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["permission.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def update_permission(
    permission_id: UUID,
    permission_in: PermissionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    perm = permission_crud.get(db, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    updated = permission_crud.update(db, perm, permission_in)

    return build_api_response(
        request, current_user, PermissionOut.model_validate(updated)
    ).model_dump()


# ---------------------
# Delete Permission
# ---------------------
@router.delete(
    "/{permission_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["permission.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def delete_permission(
    permission_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    perm = permission_crud.delete(db, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    return build_api_response(
        request, current_user, PermissionOut.model_validate(perm)
    ).model_dump()
