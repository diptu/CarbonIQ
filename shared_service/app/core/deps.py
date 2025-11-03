# shared_service/app/core/deps.py
from typing import Callable, List
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from shared_service.app.core.config import settings
from shared_service.app.utils.jwt_utils import decode_token
from user_service.app.db.session import get_db
from user_service.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Extract and return the current authenticated user from JWT token.
    Handles UUID conversion for the user ID.
    Includes debug prints to track JWT payload and potential errors.
    """
    try:
        payload = decode_token(token, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        print("DEBUG: JWT payload:", payload)  # <-- Debugging JWT payload
        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        # Convert string to UUID for DB lookup
        user_id = UUID(user_id_str)
        print("DEBUG: User ID as UUID:", user_id)  # <-- Debugging UUID conversion
    except (JWTError, ValueError) as exc:
        print("DEBUG: JWT decode or UUID conversion error:", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"DEBUG: User not found in DB for ID {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    print(f"DEBUG: Current user loaded: {user.email}")
    return user


def require_permissions(permissions: List[str]) -> Callable[[User], User]:
    """
    Dependency to check if the current_user has all required permissions.
    Works with unified UserRolePermission table.
    """

    def checker(current_user: User = Depends(get_current_user)) -> User:
        # Gather all permissions from current_user assignments
        user_perms = {
            a.permission.name for a in current_user.assignments if a.permission
        }
        print("DEBUG: User permissions:", user_perms)  # <-- Debugging permissions

        # Check if any required permission is missing
        missing = [perm for perm in permissions if perm not in user_perms]
        if missing:
            print("DEBUG: Missing required permissions:", missing)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {missing}",
            )
        return current_user

    return checker
