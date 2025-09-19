# FILE: ima_service/app/api/v1/users/router.py
"""Users API router (async)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status

from .schemas import UserCreate, UserRead, UserUpdate
from .services.base import UserService
from .services.server import get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    svc: UserService = Depends(get_user_service),
) -> UserRead:
    """Create a new user."""
    try:
        return await svc.create(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    svc: UserService = Depends(get_user_service),
) -> UserRead:
    """Fetch a user by ID."""
    user = await svc.get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    payload: UserUpdate,
    svc: UserService = Depends(get_user_service),
) -> UserRead:
    """Partially update a user (email excluded)."""
    return await svc.update(user_id, payload)


@router.post(
    "/{user_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def deactivate_user(
    user_id: str,
    svc: UserService = Depends(get_user_service),
) -> Response:
    """Deactivate a user (idempotent)."""
    await svc.deactivate(user_id)
    # Explicitly return an empty response so FastAPI won't serialize a body
    return Response(status_code=status.HTTP_204_NO_CONTENT)
