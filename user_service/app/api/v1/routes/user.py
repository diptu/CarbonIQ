# app/api/v1/routes/user.py
"""User API routes for managing user creation, retrieval, and verification."""

from datetime import datetime, timezone
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from passlib.context import CryptContext
from pydantic import BaseModel
from shared_service.app.core.deps import get_current_user, require_permissions
from shared_service.app.utils.response import APIResponse, MetaInfo, UserContext
from sqlalchemy.orm import Session

from user_service.app.core.response import build_response_from_request
from user_service.app.crud.user import user_crud
from user_service.app.db.session import get_db
from user_service.app.models.user import User
from user_service.app.schemas.user import UserCreate

router = APIRouter(prefix="/users", tags=["users"])


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: str
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#  ---------------------
# Create user
# ---------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(permissions=["user.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def create_user(
    request: Request,
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new user if the email is not already registered."""
    db_user: Optional[User] = user_crud.get_by_email(db, user_in.email)

    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {user_in.email} already exists.",
        )

    user: User = user_crud.create(db, user_in)

    # Build response
    roles = list({a.role.name for a in current_user.assignments if a.role})
    permissions = list({a.permission.name for a in current_user.assignments if a.permission})

    response = APIResponse(
        timestamp=datetime.now(timezone.utc),  # ✅ Fix: required datetime
        trace_id=getattr(request.state, "trace_id", None),
        correlation_id=getattr(request.state, "correlation_id", None),
        path=request.url.path,
        method=request.method,
        status_code=status.HTTP_201_CREATED,
        success=True,
        user_context=UserContext(
            user_id=str(current_user.id),
            tenant_id=getattr(current_user, "tenant_id", None),
            roles=roles,
            permissions=permissions,
        ),
        result={"id": str(user.id), "email": user.email},
        meta=MetaInfo(request_duration_ms=None, source="user_service"),
    )

    return response


import time

# ---------------------
# List Users
# ---------------------


@router.get(
    "/",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def list_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    """Retrieve a paginated list of users with previous/next page info."""

    start_time = time.perf_counter()  # Start measuring

    # Total number of users
    total_users = user_crud.count(db)

    # Fetch users
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

    # Pagination calculation
    next_page = skip + limit if skip + limit < total_users else None
    previous_page = skip - limit if skip - limit >= 0 else None

    # Deduplicate roles and permissions
    roles = list({a.role.name for a in current_user.assignments if a.role})
    permissions = list({a.permission.name for a in current_user.assignments if a.permission})

    # Calculate request duration in milliseconds
    request_duration_ms = (time.perf_counter() - start_time) * 1000

    response = APIResponse(
        trace_id=getattr(request.state, "trace_id", None),
        correlation_id=getattr(request.state, "correlation_id", None),
        timestamp=datetime.now(timezone.utc),
        success=True,
        status_code=status.HTTP_200_OK,
        path=request.url.path,
        method=request.method,
        api_version="v1",
        user_context=UserContext(
            user_id=str(current_user.id),
            tenant_id=getattr(current_user, "tenant_id", None),
            roles=roles,
            permissions=permissions,
        ),
        result={
            "users": users_data,
            "count": total_users,
            "perPage": limit,
            "previousPage": previous_page,
            "nextPage": next_page,
        },
        meta=MetaInfo(request_duration_ms=request_duration_ms, source="user_service"),
    )

    return response


# ---------------------
# verify user
# ---------------------
@router.post("/verify")
def verify_user(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Verify user credentials.
    Called by Auth Service during login.
    Includes roles, permissions, and tenant_id for RBAC.
    """
    email = payload.email
    password = payload.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = user_crud.get_by_email(db, email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Extract roles and permissions from user assignments
    roles = list({a.role.name for a in user.assignments if a.role})
    permissions = list({a.permission.name for a in user.assignments if a.permission})
    tenant_id = getattr(user, "tenant_id", None)

    return build_response_from_request(
        request,
        data={
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
            "roles": roles,
            "permissions": permissions,
            "tenant_id": tenant_id,
        },
    )


# ---------------------
# Get single user
# ---------------------


@router.get(
    "/{user_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def get_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single user by ID."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format. Must be a valid UUID.",
        )

    user = user_crud.get(db, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    user_data = {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_superuser": user.is_superuser,
    }

    # ✅ Deduplicate roles and permissions
    roles = list({a.role.name for a in current_user.assignments if a.role})
    permissions = list({a.permission.name for a in current_user.assignments if a.permission})

    response = APIResponse(
        trace_id=getattr(request.state, "trace_id", None),
        correlation_id=getattr(request.state, "correlation_id", None),
        path=request.url.path,
        method=request.method,
        status_code=status.HTTP_200_OK,
        success=True,
        user_context=UserContext(
            user_id=str(current_user.id),
            tenant_id=getattr(current_user, "tenant_id", None),
            roles=roles,
            permissions=permissions,
        ),
        result=user_data,
        meta=MetaInfo(request_duration_ms=None, source="user_service"),
    )

    return response


# ---------------------
# Update user
# ---------------------
@router.put(
    "/{user_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def update_user(
    user_id: str,
    user_in: UserCreate,  # you can create a separate schema for update if needed
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    """Update a user's info by ID."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = user_crud.get(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user = user_crud.update(db, user, user_in)

    roles = list({a.role.name for a in current_user.assignments if a.role})
    permissions = list({a.permission.name for a in current_user.assignments if a.permission})

    return APIResponse(
        timestamp=datetime.now(timezone.utc),
        trace_id=getattr(request.state, "trace_id", None),
        correlation_id=getattr(request.state, "correlation_id", None),
        path=request.url.path,
        method=request.method,
        status_code=status.HTTP_200_OK,
        success=True,
        user_context=UserContext(
            user_id=str(current_user.id),
            tenant_id=getattr(current_user, "tenant_id", None),
            roles=roles,
            permissions=permissions,
        ),
        result={"id": str(user.id), "email": user.email},
        meta=MetaInfo(request_duration_ms=None, source="user_service"),
    )


# ---------------------
# Delete user
# ---------------------
@router.delete(
    "/{user_id}",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["user.delete"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    """Delete a user by ID."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = user_crud.get(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_crud.delete(db, user_uuid)

    roles = list({a.role.name for a in current_user.assignments if a.role})
    permissions = list({a.permission.name for a in current_user.assignments if a.permission})

    return APIResponse(
        timestamp=datetime.now(timezone.utc),
        trace_id=getattr(request.state, "trace_id", None),
        correlation_id=getattr(request.state, "correlation_id", None),
        path=request.url.path,
        method=request.method,
        status_code=status.HTTP_200_OK,
        success=True,
        user_context=UserContext(
            user_id=str(current_user.id),
            tenant_id=getattr(current_user, "tenant_id", None),
            roles=roles,
            permissions=permissions,
        ),
        result={"message": f"User {user.email} deleted successfully"},
        meta=MetaInfo(request_duration_ms=None, source="user_service"),
    )


# ---------------------
# Activate user
# ---------------------
@router.post(
    "/{user_id}/activate",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def activate_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    """Activate a user by ID."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = user_crud.get(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_crud.activate(db, user_uuid)

    roles = list({a.role.name for a in current_user.assignments if a.role})
    permissions = list({a.permission.name for a in current_user.assignments if a.permission})

    return APIResponse(
        timestamp=datetime.now(timezone.utc),
        trace_id=getattr(request.state, "trace_id", None),
        correlation_id=getattr(request.state, "correlation_id", None),
        path=request.url.path,
        method=request.method,
        status_code=status.HTTP_200_OK,
        success=True,
        user_context=UserContext(
            user_id=str(current_user.id),
            tenant_id=getattr(current_user, "tenant_id", None),
            roles=roles,
            permissions=permissions,
        ),
        result={"message": f"User {user.email} activated successfully"},
        meta=MetaInfo(request_duration_ms=None, source="user_service"),
    )


# ---------------------
# Deactivate user
# ---------------------
@router.post(
    "/{user_id}/deactivate",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(permissions=["user.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def deactivate_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    """Deactivate a user by ID."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = user_crud.get(db, user_uuid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_crud.deactivate(db, user_uuid)

    roles = list({a.role.name for a in current_user.assignments if a.role})
    permissions = list({a.permission.name for a in current_user.assignments if a.permission})

    return APIResponse(
        timestamp=datetime.now(timezone.utc),
        trace_id=getattr(request.state, "trace_id", None),
        correlation_id=getattr(request.state, "correlation_id", None),
        path=request.url.path,
        method=request.method,
        status_code=status.HTTP_200_OK,
        success=True,
        user_context=UserContext(
            user_id=str(current_user.id),
            tenant_id=getattr(current_user, "tenant_id", None),
            roles=roles,
            permissions=permissions,
        ),
        result={"message": f"User {user.email} deactivated successfully"},
        meta=MetaInfo(request_duration_ms=None, source="user_service"),
    )
