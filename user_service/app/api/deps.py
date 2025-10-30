"""Dependencies for role and permission checking."""

from typing import List, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User

LogicType = Literal["AND", "OR"]

# This assumes you’re using OAuth2 with JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Extract and return the current authenticated user from JWT token.

    Raises:
        HTTPException: If token is invalid or user does not exist.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_roles_permissions(
    roles: List[str] = [], permissions: List[str] = [], logic: LogicType = "OR"
):
    """
    Dependency to check if current_user satisfies roles and permissions with AND / OR logic.

    Args:
        roles (List[str]): Required roles.
        permissions (List[str]): Required permissions.
        logic (Literal["AND", "OR"]): Use "AND" (all required) or "OR" (any one).
    """

    def checker(current_user: User = Depends(get_current_user)):
        user_roles = [r.role.name for r in current_user.roles]
        user_perms = [p.permission.name for p in current_user.user_permissions]

        role_check = (
            all(role in user_roles for role in roles)
            if logic == "AND"
            else any(role in user_roles for role in roles)
        )
        perm_check = (
            all(perm in user_perms for perm in permissions)
            if logic == "AND"
            else any(perm in user_perms for perm in permissions)
        )

        if logic == "AND":
            if not (role_check and perm_check):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires roles {roles} AND permissions {permissions}",
                )
        else:  # OR logic
            if not (role_check or perm_check):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires roles {roles} OR permissions {permissions}",
                )
        return current_user

    return checker
