"""API routes for managing UserRole assignments using build_api_response formatting."""

import time
from functools import wraps
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from shared_service.app.core.deps import get_cached_current_user, require_permissions
from shared_service.app.utils.response import APIResponse, build_api_response
from sqlalchemy.orm import Session

from user_service.app.crud.user_role import user_role_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.user_role import UserRoleCreate, UserRoleRead

router = APIRouter(prefix="/user-roles", tags=["user_roles"])


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
def fetch_user_role_or_404(user_role_id: UUID, db: Session):
    ur = user_role_crud.get(db, user_role_id)
    if not ur:
        raise HTTPException(status_code=404, detail="User-Role assignment not found")
    return ur


# ---------------------
# Create UserRole
# ---------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(permissions=["user_role.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def create_user_role(
    user_role_in: UserRoleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    ur = user_role_crud.create(db, user_role_in)
    return build_api_response(request, current_user, UserRoleRead.model_validate(ur)).model_dump()


# ---------------------
# Get Single UserRole
# ---------------------
@router.get(
    "/{user_role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["user_role.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def get_user_role(
    user_role_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    ur = fetch_user_role_or_404(user_role_id, db)
    return build_api_response(request, current_user, UserRoleRead.model_validate(ur)).model_dump()


# ---------------------
# List UserRoles
# ---------------------
@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["user_role.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def list_user_roles(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    total = user_role_crud.count(db)
    user_roles = user_role_crud.get_all(db, skip=skip, limit=limit)
    user_roles_data = [UserRoleRead.model_validate(ur) for ur in user_roles]

    result = {
        "user_roles": user_roles_data,
        "count": total,
        "perPage": limit,
        "previousPage": skip - limit if skip - limit >= 0 else None,
        "nextPage": skip + limit if skip + limit < total else None,
    }

    return build_api_response(request, current_user, result).model_dump()


# ---------------------
# Delete UserRole
# ---------------------
@router.delete(
    "/{user_role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["user_role.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def delete_user_role(
    user_role_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    fetch_user_role_or_404(user_role_id, db)
    deleted_ur = user_role_crud.delete(db, user_role_id)
    return build_api_response(
        request, current_user, UserRoleRead.model_validate(deleted_ur)
    ).model_dump()
