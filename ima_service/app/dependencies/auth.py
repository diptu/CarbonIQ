# app/dependencies/auth.py
"""Authentication dependencies for FastAPI.

Includes:
- OAuth2PasswordBearer token parsing
- Current user resolution
- Tenant-aware authentication
"""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.core.config import get_settings
from app.dependencies.db import get_db
from app.models.user import User

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get the current user from JWT token.

    Args
    ----
    token : str
        Bearer token from request header
    db : Session
        Database session

    Returns
    -------
    User
        Authenticated user instance

    Raises
    ------
    HTTPException
        If token is invalid or user not found
    """
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    tenant_id: Optional[str] = payload.get("tenant_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = (
        db.query(User).filter(User.id == user_id, User.tenant_id == tenant_id).first()
    )
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return user
