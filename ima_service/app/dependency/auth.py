# ima_service/app/dependency/auth.py
"""Authentication dependency for FastAPI routes."""

from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import verify_token  # type:ignore[import-not-found]
from app.dependency.db import get_async_db  # type:ignore[import-not-found]
from app.models.user import User  # type:ignore[import-not-found]


async def get_current_user(
    token: str, db: AsyncSession = Depends(get_async_db)
) -> User:
    """Get current authenticated user from JWT token."""
    payload: Optional[dict] = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user_id: UUID = UUID(payload.get("user_id"))
    result = await db.execute(select(User).where(User.id == user_id))
    user: Optional[User] = result.scalars().first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user"
        )

    return user
