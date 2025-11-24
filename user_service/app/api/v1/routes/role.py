"""API routes for managing roles using build_api_response formatting with AsyncSession."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from shared_service.app.core.deps import get_cached_current_user, require_permissions
from shared_service.app.utils.fetch import fetch_or_404
from shared_service.app.utils.paggination import paginate
from shared_service.app.utils.response import APIResponse, build_api_response
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.app.core.config import settings
from user_service.app.crud.role import role_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.role import RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


# ---------------------
# Dependency: Fetch user or 404
# ---------------------
async def fetch_role_or_404(user_id: UUID, db: AsyncSession = Depends(get_db)) -> User:
    return await fetch_or_404(role_crud.get, db, user_id)


# ---------------------
# Create Role
# ---------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(["role.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def create_role(
    role_in: RoleCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    existing_role = await role_crud.get_by_name(db, role_in.name)
    if existing_role:
        raise HTTPException(status_code=409, detail="Role already exists")

    role = await role_crud.create(db, role_in)
    return build_api_response(request, current_user, RoleOut.model_validate(role))


# ---------------------
# Get Single Role
# ---------------------
@router.get(
    "/{role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def get_role(
    role_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    role = await fetch_role_or_404(role_id, db)
    return build_api_response(request, current_user, RoleOut.model_validate(role))


# ---------------------
# List Roles
# ---------------------
@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def list_roles(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    total_roles = await role_crud.count(db)
    roles = await role_crud.get_all(db, skip=skip, limit=limit) or []
    roles_data = [RoleOut.model_validate(r) for r in roles]
    pagination = paginate(skip=skip, limit=limit, total=total_roles)
    result = {"roles": roles_data, **pagination}

    return build_api_response(request, current_user, result, status_code=status.HTTP_200_OK)


# ---------------------
# Update Role
# ---------------------
@router.put(
    "/{role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def update_role(
    role_id: UUID,
    role_in: RoleUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    role = await fetch_role_or_404(role_id, db)
    # Check for duplicate name
    if role.name:
        existing = await role_crud.get_by_name(db, role_in.name)
        if existing and existing.id != role_id:
            raise HTTPException(
                status_code=409,
                detail=f"Permission with name '{role_in.name}' already exists",
            )

    updated_role = await role_crud.update(db, role, role_in)
    return build_api_response(request, current_user, RoleOut.model_validate(updated_role))


# ---------------------
# Delete Role
# ---------------------
@router.delete(
    "/{role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["role.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def delete_role(
    role_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    role = await fetch_role_or_404(role_id, db)
    await role_crud.delete(db, role_id)

    return build_api_response(
        request,
        current_user,
        result={"message": f"Role {role_id} deleted successfully"},
        status_code=status.HTTP_200_OK,
    )
