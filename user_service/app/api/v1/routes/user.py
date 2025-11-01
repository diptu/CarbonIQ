# app/api/v1/routes/user.py
"""User API routes for managing user creation, retrieval, and verification."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permissions
from app.core.response import build_response
from app.crud.user import user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate

router = APIRouter(prefix="/users", tags=["users"])


class LoginRequest(BaseModel):
    """Request schema for user login."""

    email: str
    password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(permissions=["user.create"]))],
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new user if the email is not already registered."""
    db_user: Optional[User] = user_crud.get_by_email(db, user_in.email)

    # Roles and permissions for current_user
    roles = list({a.role.name for a in current_user.assignments if a.role})
    permissions = list({a.permission.name for a in current_user.assignments if a.permission})

    if db_user is not None:
        # Returning existing user data if email already exists
        return build_response(
            data={"id": str(db_user.id), "email": db_user.email},
            user_id=current_user.id,
            tenant_id=getattr(current_user, "tenant_id", None),
            roles=roles,
            permissions=permissions,
        )

    user: User = user_crud.create(db, user_in)

    return build_response(
        data={"id": str(user.id), "email": user.email},
        user_id=current_user.id,
        tenant_id=getattr(current_user, "tenant_id", None),
        roles=roles,
        permissions=permissions,
    )


@router.get(
    "/",
    dependencies=[Depends(require_permissions(permissions=["user.read"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve a paginated list of users."""
    users: List[User] = user_crud.get_all(db, skip=skip, limit=limit)
    users_data = [{"id": str(u.id), "email": u.email} for u in users]

    # Roles assigned to current user
    roles = list({a.role.name for a in current_user.assignments if a.role})

    # Permissions via roles or direct assignment
    permissions = list({a.permission.name for a in current_user.assignments if a.permission})

    return build_response(
        data=users_data,
        user_id=current_user.id,
        tenant_id=getattr(current_user, "tenant_id", None),
        roles=roles,
        permissions=permissions,
    )


@router.post("/verify")
def verify_user(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Verify user credentials.
    Called by Auth Service during login.
    """
    email = credentials.email
    password = credentials.password

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = user_crud.get_by_email(db, email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_superuser": user.is_superuser,
    }
