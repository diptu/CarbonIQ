from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_permission import user_permission_crud
from app.db.session import get_db
from app.schemas.user_permission import UserPermissionCreate, UserPermissionRead

router = APIRouter(prefix="/user-permissions", tags=["user_permissions"])


@router.post("/", response_model=UserPermissionRead, status_code=status.HTTP_201_CREATED)
def assign_permission(user_perm_in: UserPermissionCreate, db: Session = Depends(get_db)):
    return user_permission_crud.create(db, user_perm_in)


@router.get("/", response_model=list[UserPermissionRead])
def list_user_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_permission_crud.get_all(db, skip=skip, limit=limit)


@router.delete("/{user_permission_id}", response_model=UserPermissionRead)
def delete_user_permission(user_permission_id: UUID, db: Session = Depends(get_db)):
    user_perm = user_permission_crud.delete(db, user_permission_id)
    if not user_perm:
        raise HTTPException(status_code=404, detail="UserPermission not found")
    return user_perm
