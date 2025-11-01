"""Dependencies for role and permission checking."""

from typing import Callable, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Extract and return the current authenticated user from JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_permissions(permissions: List[str]) -> Callable[[User], User]:
    """
    Dependency to check if the current_user has all required permissions.

    Works with unified UserRolePermission table:
    - Permissions can come from roles or direct user assignment.
    """

    def checker(current_user: User = Depends(get_current_user)) -> User:
        # Gather all permissions from current_user assignments
        user_perms = {a.permission.name for a in current_user.assignments if a.permission}

        # Check if any required permission is missing
        missing = [perm for perm in permissions if perm not in user_perms]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {missing}",
            )
        return current_user

    return checker
