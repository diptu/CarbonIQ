"""User API routes for managing user creation and retrieval."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permissions
from app.core.response import build_response
from app.crud.user import user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate

router = APIRouter(prefix="/users", tags=["users"])


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

    if db_user is not None:
        # Returning existing user data if email already exists
        return build_response(
            data={"id": str(db_user.id), "email": db_user.email},
            user_id=current_user.id,
            tenant_id=getattr(current_user, "tenant_id", None),
            roles=[r.role.name for r in current_user.roles],
            permissions=[p.permission.name for p in current_user.permissions],
        )

    user: User = user_crud.create(db, user_in)

    return build_response(
        data={"id": str(user.id), "email": user.email},
        user_id=current_user.id,
        tenant_id=getattr(current_user, "tenant_id", None),
        roles=[r.role.name for r in current_user.roles],
        permissions=[p.permission.name for p in current_user.permissions],
    )


@router.get(
    "/",
    dependencies=[Depends(require_permissions(permissions=["user.read"]))],
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

    return build_response(
        data=users_data,
        user_id=current_user.id,
        tenant_id=getattr(current_user, "tenant_id", None),
        roles=[r.role.name for r in current_user.roles],
        permissions=[p.permission.name for p in current_user.permissions],
    )
