"""API routes for managing roles using build_api_response formatting."""

import time
from functools import wraps
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from shared_service.app.core.deps import get_current_user, require_permissions
from shared_service.app.utils.response import APIResponse, build_api_response
from sqlalchemy.orm import Session

from user_service.app.crud.role import role_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.role import RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


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


# ---------------------------------------------------
# Cached current_user to avoid repeated DB hits
# ---------------------------------------------------
def get_cached_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    if hasattr(request.state, "current_user"):
        return request.state.current_user

    user = get_current_user(db=db)
    request.state.current_user = user
    return user


# ---------------------------------------------------
# Reusable fetch
# ---------------------------------------------------
def fetch_role_or_404(role_id: UUID, db: Session):
    role = role_crud.get(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


# ---------------------
# Create Role
# ---------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(permissions=["role.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def create_role(
    role_in: RoleCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    if role_crud.get_by_name(db, role_in.name):
        raise HTTPException(status_code=400, detail="Role already exists")

    role = role_crud.create(db, role_in)
    return build_api_response(request, current_user, RoleOut.model_validate(role)).model_dump()


# ---------------------
# Get Single Role
# ---------------------
@router.get(
    "/{role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["role.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def get_role(
    role_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    role = fetch_role_or_404(role_id, db)
    return build_api_response(request, current_user, RoleOut.model_validate(role)).model_dump()


# ---------------------
# List Roles
# ---------------------
@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["role.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def list_roles(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    total_roles = role_crud.count(db)
    roles = role_crud.get_all(db, skip=skip, limit=limit)
    roles_data = [RoleOut.model_validate(r) for r in roles]

    result = {
        "roles": roles_data,
        "count": total_roles,
        "perPage": limit,
        "previousPage": skip - limit if skip - limit >= 0 else None,
        "nextPage": skip + limit if skip + limit < total_roles else None,
    }

    return build_api_response(request, current_user, result).model_dump()


# ---------------------
# Update Role
# ---------------------
@router.put(
    "/{role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["role.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def update_role(
    role_id: UUID,
    role_in: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    role = fetch_role_or_404(role_id, db)
    updated_role = role_crud.update(db, role, role_in)
    return build_api_response(
        request, current_user, RoleOut.model_validate(updated_role)
    ).model_dump()


# ---------------------
# Delete Role
# ---------------------
@router.delete(
    "/{role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["role.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def delete_role(
    role_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    fetch_role_or_404(role_id, db)
    deleted_role = role_crud.delete(db, role_id)
    return build_api_response(
        request, current_user, RoleOut.model_validate(deleted_role)
    ).model_dump()
