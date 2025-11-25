"""API routes for managing UserRole assignments using build_api_response formatting with AsyncSession."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from shared_service.app.core.deps import get_cached_current_user, require_permissions
from shared_service.app.utils.fetch import fetch_or_404
from shared_service.app.utils.paggination import paginate
from shared_service.app.utils.response import APIResponse, build_api_response
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.app.api.v1.routes.docs.user_roles import (
    CREATE_USER_ROLE_DOCS,
    DELETE_USER_ROLE_DOCS,
    GET_USER_ROLE_DOCS,
    LIST_USER_ROLES_DOCS,
)
from user_service.app.core.config import settings
from user_service.app.crud.user_role import user_role_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.user_role import UserRoleCreate, UserRoleRead

router = APIRouter(prefix="/user-roles", tags=["user_roles"])


# ---------------------
# Dependency: Fetch user_role or 404
# ---------------------
async def fetch_user_role_or_404(
    user_role_id: UUID, db: AsyncSession = Depends(get_db)
) -> UserRoleRead:
    return await fetch_or_404(user_role_crud.get, db, user_role_id)


# ---------------------
# Create UserRole
# ---------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(["user_role.create"]))],
    openapi_extra={**CREATE_USER_ROLE_DOCS, "security": [{"BearerAuth": []}]},
)
async def create_user_role(
    user_role_in: UserRoleCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    # Prevent duplicate assignment
    existing = await user_role_crud.get_by_user_role(db, user_role_in.user_id, user_role_in.role_id)
    if existing:
        raise HTTPException(status_code=409, detail="UserRole assignment already exists")

    ur = await user_role_crud.create(db, user_role_in)
    payload = {
        "id": str(ur.id),
        "user_id": str(ur.user_id),
        "role_id": str(ur.role_id),
    }

    return build_api_response(request, current_user, payload, status_code=status.HTTP_201_CREATED)


# ---------------------
# Get Single UserRole
# ---------------------
@router.get(
    "/{user_role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user_role.read"]))],
    openapi_extra={**GET_USER_ROLE_DOCS, "security": [{"BearerAuth": []}]},
)
async def get_user_role(
    user_role_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    ur = await fetch_user_role_or_404(user_role_id, db)
    return build_api_response(request, current_user, UserRoleRead.model_validate(ur))


# ---------------------
# List UserRoles
# ---------------------
@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user_role.read"]))],
    openapi_extra={**LIST_USER_ROLES_DOCS, "security": [{"BearerAuth": []}]},
)
async def list_user_roles(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    total_user_roles = await user_role_crud.count(db)
    user_roles = await user_role_crud.get_all(db, skip=skip, limit=limit) or []
    user_roles_data = [UserRoleRead.model_validate(ur) for ur in user_roles]
    pagination = paginate(skip=skip, limit=limit, total=total_user_roles)

    result = {"user_roles": user_roles_data, **pagination}
    return build_api_response(request, current_user, result, status_code=status.HTTP_200_OK)


# ---------------------
# Delete UserRole
# ---------------------
@router.delete(
    "/{user_role_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user_role.delete"]))],
    openapi_extra={**DELETE_USER_ROLE_DOCS, "security": [{"BearerAuth": []}]},
)
async def delete_user_role(
    user_role_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    ur = await fetch_user_role_or_404(user_role_id, db)
    await user_role_crud.delete(db, user_role_id)

    return build_api_response(
        request,
        current_user,
        result={"message": f"UserRole {user_role_id} deleted successfully"},
        status_code=status.HTTP_200_OK,
    )
