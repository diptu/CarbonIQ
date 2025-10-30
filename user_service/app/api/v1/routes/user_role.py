from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_role import user_role_crud
from app.db.session import get_db
from app.schemas.user_role import UserRoleCreate, UserRoleOut

router = APIRouter(prefix="/user-roles", tags=["user_roles"])


@router.post("/", response_model=UserRoleOut, status_code=status.HTTP_201_CREATED)
def assign_role(user_role_in: UserRoleCreate, db: Session = Depends(get_db)):
    return user_role_crud.create(db, user_role_in)


@router.get("/", response_model=list[UserRoleOut])
def list_user_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_role_crud.get_all(db, skip=skip, limit=limit)


@router.delete("/{user_role_id}", response_model=UserRoleOut)
def delete_user_role(user_role_id: UUID, db: Session = Depends(get_db)):
    user_role = user_role_crud.delete(db, user_role_id)
    if not user_role:
        raise HTTPException(status_code=404, detail="UserRole not found")
    return user_role
