# FILE: ima_service/app/api/v1/users/services/server.py
"""FastAPI DI wiring for user services (async)."""

from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ima_service.app.db.session import get_db  # ✅ async dep, defined in repo

from .base import UserService
from .database import DatabaseUserService


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """Provide a DatabaseUserService via FastAPI DI."""
    return DatabaseUserService(db=db)
