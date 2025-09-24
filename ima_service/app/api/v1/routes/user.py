# ima_service/app/api/v1/routes/user.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ima_service.app.db.session import get_db
from ima_service.app.crud import user as crud
from ima_service.app.schemas.user import UserRead, UserCreate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await crud.create_user(db=db, user=user)


@router.get("/", response_model=List[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
):
    return await crud.get_users(db, skip=skip, limit=limit, is_active=is_active)


@router.get("/{user_id}", response_model=UserRead)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch("/{user_id}/deactivate", response_model=UserRead)
async def deactivate_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.deactivate_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.patch("/{user_id}/reactivate", response_model=UserRead)
async def reactivate_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = await crud.reactivate_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
