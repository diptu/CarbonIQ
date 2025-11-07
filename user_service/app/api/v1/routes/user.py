# app/api/v1/routes/user.py
"""User API routes for managing users with cached current_user."""

import time
from functools import wraps
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from passlib.context import CryptContext
from pydantic import BaseModel
from shared_service.app.core.deps import get_current_user, require_permissions
from shared_service.app.utils.response import APIResponse, build_api_response
from sqlalchemy.orm import Session

from user_service.app.crud.user import user_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.user import UserCreate

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: str
    password: str


def extract_roles_permissions(user: User):
    """
    Return sorted roles and permissions for a user.

    - Roles come from user_roles.
    - Permissions come from role_permissions linked to each role.
    """
    roles = user.roles_cached
    permissions = user.permissions_cached

    # for role in user.roles:
    #     for rp in role.role_permissions:
    #         if rp.permission:
    #             permissions_set.add(rp.permission.name)

    # permissions = sorted(permissions_set)
    return roles, permissions


def request_timer(func):
    """Decorator to measure request duration in ms and attach to meta."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        response: APIResponse = await func(*args, **kwargs)
        response.meta.request_duration_ms = (time.perf_counter() - start_time) * 1000
        return response

    return wrapper


def get_cached_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """Cache current_user per request to avoid repeated DB queries."""
    if hasattr(request.state, "current_user"):
        return request.state.current_user
    user = get_current_user(db=db)
    request.state.current_user = user
    return user


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
@request_timer
async def create_user(
    request: Request,
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
) -> APIResponse:
    if user_crud.get_by_email(db, user_in.email):
        raise HTTPException(
            status_code=400, detail=f"User with email {user_in.email} already exists."
        )

    user = user_crud.create(db, user_in)

    return build_api_response(
        request=request,
        current_user=current_user,
        result={"id": str(user.id), "email": user.email},
        status_code=status.HTTP_201_CREATED,
        meta_extra={"source": "user_service"},
    )


# ---------------------
# List Users
# ---------------------
@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def list_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
) -> APIResponse:
    total_users = user_crud.count(db)
    users: List[User] = user_crud.get_all(db, skip=skip, limit=limit)
    users_data = [
        {
            "id": str(u.id),
            "email": u.email,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "is_superuser": u.is_superuser,
        }
        for u in users
    ]

    pagination = {
        "count": total_users,
        "perPage": limit,
        "previousPage": skip - limit if skip - limit >= 0 else None,
        "nextPage": skip + limit if skip + limit < total_users else None,
    }

    return build_api_response(
        request=request,
        current_user=current_user,
        result={"users": users_data, **pagination},
        status_code=status.HTTP_200_OK,
        meta_extra={"source": "user_service"},
    )


# ---------------------
# Verify user
# ---------------------
@router.post("/verify", response_model=APIResponse)
@request_timer
async def verify_user(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """Verify user credentials for login, includes roles, permissions, tenant_id."""
    email = payload.email
    password = payload.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = user_crud.get_by_email(db, email)
    print(f"user: {user}")
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    roles, permissions = extract_roles_permissions(user)

    return build_api_response(
        request=request,
        current_user=user,
        result={
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
            "roles": roles,
            "permissions": permissions,
            "tenant_id": getattr(user, "tenant_id", None),
        },
        status_code=200,
        success=True,
        meta_extra={"source": "user_service"},
    )


# ---------------------
# Shared UUID parsing and user fetching
# ---------------------
def fetch_user_or_404(user_id: str, db: Session) -> User:
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    user = user_crud.get(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------------------
# Get single user
# ---------------------
@router.get(
    "/{user_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def get_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    user = fetch_user_or_404(user_id, db)
    return build_api_response(
        request=request,
        current_user=current_user,
        result={
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
        },
        status_code=200,
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
@request_timer
async def update_user(
    user_id: str,
    user_in: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    user = fetch_user_or_404(user_id, db)
    user = user_crud.update(db, user, user_in)
    return build_api_response(
        request=request,
        current_user=current_user,
        result={"id": str(user.id), "email": user.email},
        status_code=200,
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
@request_timer
async def delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    user = fetch_user_or_404(user_id, db)
    user_crud.delete(db, user.id)
    return build_api_response(
        request=request,
        current_user=current_user,
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
@request_timer
async def activate_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    user = fetch_user_or_404(user_id, db)
    user_crud.activate(db, user.id)
    return build_api_response(
        request=request,
        current_user=current_user,
        result={"message": f"User {user.email} activated successfully"},
        status_code=200,
    )


# ---------------------
# Deactivate user
# ---------------------
@router.post(
    "/{user_id}/deactivate",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def deactivate_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_cached_current_user),
):
    user = fetch_user_or_404(user_id, db)
    user_crud.deactivate(db, user.id)
    return build_api_response(
        request=request,
        current_user=current_user,
        result={"message": f"User {user.email} deactivated successfully"},
        status_code=200,
    )
