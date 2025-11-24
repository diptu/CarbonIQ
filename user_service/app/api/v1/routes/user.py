# app/api/v1/routes/user.py
from uuid import UUID

from auth_service.app.schemas.auth import LoginRequest
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from passlib.context import CryptContext
from shared_service.app.core.deps import get_cached_current_user, require_permissions
from shared_service.app.utils.fetch import fetch_or_404
from shared_service.app.utils.paggination import paginate
from shared_service.app.utils.response import APIResponse, build_api_response
from sqlalchemy.ext.asyncio import AsyncSession

from user_service.app.core.config import settings
from user_service.app.crud.user import user_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------
# Dependency: Fetch user or 404
# ---------------------
async def get_user_or_404(user_id: UUID, db: AsyncSession = Depends(get_db)) -> User:
    return await fetch_or_404(user_crud.get, db, user_id)


# ---------------------
# Create user
# ---------------------
@router.post(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    request: Request,
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
) -> APIResponse:
    existing_user = await user_crud.get_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user_in.email} already exists.",
        )
    user = await user_crud.create(db, user_in)
    return build_api_response(
        request=request,
        current_user=current_user,
        result=UserRead.model_validate(user),
        status_code=status.HTTP_201_CREATED,
        meta_extra={"source": "user_service"},
    )


# ---------------------
# List users
# ---------------------
@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def list_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(settings.DEFAULT_PAGE_LIMIT, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
) -> APIResponse:
    total_users = await user_crud.count(db)
    users = await user_crud.get_all(db, skip=skip, limit=limit)
    users_data = [UserRead.model_validate(u) for u in users]
    pagination = paginate(skip=skip, limit=limit, total=total_users)
    return build_api_response(
        request=request,
        result={"users": users_data, **pagination},
        status_code=status.HTTP_200_OK,
        meta_extra={"source": "user_service"},
    )


# ---------------------
# Verify user
# ---------------------
@router.post(
    "/verify",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
async def verify_user(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> APIResponse:
    if not payload.email or not payload.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    user = await user_crud.get_by_email_with_roles(db, payload.email)
    if not user or not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    roles, permissions = user.roles_cached, user.permissions_cached
    return build_api_response(
        request=request,
        current_user=user,
        result={
            **UserRead.model_validate(user).model_dump(),
            "roles": roles,
            "permissions": permissions,
        },
        status_code=200,
        success=True,
        meta_extra={"source": "user_service"},
    )


# ---------------------
# Get single user
# ---------------------
@router.get(
    "/{user_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def get_user(
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
) -> APIResponse:
    user = await fetch_or_404(user_crud.get, db, user_id)
    return build_api_response(
        request=request,
        current_user=current_user,
        result=UserRead.model_validate(user),
        status_code=status.HTTP_200_OK,
    )


# ---------------------
# Update user
# ---------------------
@router.put(
    "/{user_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
) -> APIResponse:
    user = await fetch_or_404(user_crud.get, db, user_id)
    user = await user_crud.update(db, user, user_in)
    return build_api_response(
        request=request,
        current_user=current_user,
        result=UserRead.model_validate(user),
        status_code=status.HTTP_200_OK,
    )


# ---------------------
# Delete user
# ---------------------
@router.delete(
    "/{user_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def delete_user(
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    user = await fetch_or_404(user_crud.get, db, user_id)
    await user_crud.delete(db, user.id)
    return build_api_response(
        request=request,
        current_user=current_user,
        include_user_context=False,
        result={"message": f"User {user.email} deleted successfully"},
        status_code=200,
    )


# ---------------------
# Activate user
# ---------------------
@router.post(
    "/{user_id}/activate",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def activate_user(
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    user = await fetch_or_404(user_crud.get, db, user_id)
    user = await user_crud.activate(db, user.id)
    return build_api_response(
        request=request,
        current_user=current_user,
        result={"message": f"User {user.email} activated successfully"},
        status_code=200,
    )


# ---------------------
# Deactivate user
# ---------------------
@router.put(
    "/{user_id}/deactivate",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def deactivate_user(
    user_id: UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    user = await fetch_or_404(user_crud.get, db, user_id)
    user = await user_crud.deactivate(db, user.id)
    return build_api_response(
        request=request,
        current_user=current_user,
        result={"message": f"User {user.email} deactivated successfully"},
        status_code=200,
    )
