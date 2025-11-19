# shared_service/app/core/deps.py
from typing import Callable, List, Union
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from shared_service.app.core.config import settings
from shared_service.app.utils.jwt_utils import decode_token
from user_service.app.db.session import get_db
from user_service.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Union[User, dict]:
    """
    Return the current authenticated user and cache it per request.
    Works with both User objects (direct service) and dicts (gateway proxy).
    """
    # Return cached user if already fetched
    if hasattr(request.state, "current_user"):
        return request.state.current_user

    # Decode JWT and extract user ID
    try:
        payload = decode_token(token, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        user_id = UUID(user_id_str)
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc

    # Fetch user from DB
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Cache user in request.state
    request.state.current_user = user
    return user


def require_permissions(
    permissions: List[str],
) -> Callable[[Union[User, dict]], Union[User, dict]]:
    """
    Dependency to check if the current_user has all required permissions.
    Works for both User objects and JWT dicts from gateway.
    """

    def checker(
        current_user: Union[User, dict] = Depends(get_current_user),
    ) -> Union[User, dict]:
        # Determine how to access permissions
        if isinstance(current_user, dict):
            user_perms = set(current_user.get("permissions", []))
        else:
            user_perms = set(current_user.permissions_cached)

        # Raise 403 if any required permission is missing
        missing = [perm for perm in permissions if perm not in user_perms]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {missing}",
            )
        return current_user

    return checker


# ---------------------------------------------------
# Cached current_user to avoid repeated DB hits
# ---------------------------------------------------
def get_cached_current_user(
    request: Request, db: Session = Depends(get_db)
) -> Union[User, dict]:
    """
    Returns the cached current_user if available; otherwise fetches via get_current_user.
    Works for both User objects and JWT dicts.
    """
    if hasattr(request.state, "current_user"):
        return request.state.current_user

    user = get_current_user(request=request, db=db)
    request.state.current_user = user
    return user
