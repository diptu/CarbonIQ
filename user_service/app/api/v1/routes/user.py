# app/api/v1/routes/user.py
"""User API routes for managing user creation, retrieval, and verification."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from passlib.context import CryptContext
from pydantic import BaseModel
from shared_service.app.core.deps import get_current_user, require_permissions
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

# ---------------------
# create users
# ---------------------


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(permissions=["user.create"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def create_user(
    request: Request,
    user_in: UserCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new user if the email is not already registered."""
    db_user: Optional[User] = user_crud.get_by_email(db, user_in.email)

    if db_user is not None:
        # Returning existing user data if email already exists
        return build_response_from_request(
            request,
            data={"id": str(db_user.id), "email": db_user.email},
        )

    user: User = user_crud.create(db, user_in)

    return build_response_from_request(
        request,
        data={"id": str(user.id), "email": user.email},
    )


# ---------------------
# List users
# ---------------------
@router.get(
    "/",
    dependencies=[Depends(require_permissions(permissions=["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve a paginated list of users."""
    users: List[User] = user_crud.get_all(db, skip=skip, limit=limit)
    users_data = [{"id": str(u.id), "email": u.email} for u in users]

    return build_response_from_request(
        request,
        data=users_data,
    )


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
