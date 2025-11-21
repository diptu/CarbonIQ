# shared_service/app/core/deps.py
from typing import Callable, List, Optional, Union
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from shared_service.app.core.config import settings
from shared_service.app.utils.jwt_utils import decode_token
from user_service.app.db.session import get_db
from user_service.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ---------------------------------------------------
# NEW: safe tenant fetch helper
# ---------------------------------------------------
def fetch_tenant_info(user_id: str) -> Optional[dict]:
    """
    Calls tenant-service to get tenant_id for the given user_id.
    Fail-soft: returns None if service is unavailable or non-200.
    """
    url = f"{settings.TENANT_SERVICE_URL}/memberships/user/{user_id}"

    try:
        with httpx.Client(timeout=settings.TENANT_REQUEST_TIMEOUT_SECONDS) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                return resp.json()
            return None
    except httpx.RequestError:
        return None


def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Union[User, dict]:
    """
    Return current authenticated user and cache it per request.
    Now includes cached tenant_id to avoid repeated tenant-service calls.
    """
    # Return cached user if already fetched
    if hasattr(request.state, "current_user"):
        return request.state.current_user

    # Decode JWT and extract user ID
    try:
        payload = decode_token(token, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        user_id_str: Optional[str] = payload.get("sub")
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

    # ---------------------------------------------------
    # NEW: Fetch and cache tenant_id
    # ---------------------------------------------------
    if not hasattr(request.state, "tenant_id"):
        tenant_data = fetch_tenant_info(str(user_id))
        tenant_id = None
        if tenant_data and isinstance(tenant_data, dict):
            tenant_id = tenant_data.get("tenant_id")

        request.state.tenant_id = tenant_id

    # attach tenant_id to user object (runtime only)
    setattr(user, "tenant_id", request.state.tenant_id)

    # Cache combined user object
    request.state.current_user = user
    return user


def require_permissions(
    permissions: List[str],
) -> Callable[[Union[User, dict]], Union[User, dict]]:
    """
    Dependency to check if current_user has all required permissions.
    """

    def checker(
        current_user: Union[User, dict] = Depends(get_current_user),
    ) -> Union[User, dict]:
        if isinstance(current_user, dict):
            user_perms = set(current_user.get("permissions", []))
        else:
            user_perms = set(current_user.permissions_cached)

        missing = [perm for perm in permissions if perm not in user_perms]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permissions: {missing}",
            )
        return current_user

    return checker


# ---------------------------------------------------
# Cached current_user wrapper
# ---------------------------------------------------
def get_cached_current_user(
    request: Request, db: Session = Depends(get_db)
) -> Union[User, dict]:
    """
    Return cached current_user if available; otherwise fetch.
    Also returns cached tenant_id without additional network calls.
    """
    if hasattr(request.state, "current_user"):
        return request.state.current_user

    user = get_current_user(request=request, db=db)
    # user.tenant_id = fetch_tenant_info(user.user_id) or "temp"
    request.state.current_user = user
    return user
