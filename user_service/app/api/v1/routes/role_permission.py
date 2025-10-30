from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.role_permission import role_permission_crud
from app.db.session import get_db
from app.schemas.role_permission import RolePermissionCreate, RolePermissionRead

router = APIRouter(prefix="/role-permissions", tags=["role_permissions"])


@router.post("/", response_model=RolePermissionRead, status_code=status.HTTP_201_CREATED)
def assign_permission_to_role(role_perm_in: RolePermissionCreate, db: Session = Depends(get_db)):
    return role_permission_crud.create(db, role_perm_in)


@router.get("/", response_model=list[RolePermissionRead])
def list_role_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return role_permission_crud.get_all(db, skip=skip, limit=limit)


@router.delete("/{role_permission_id}", response_model=RolePermissionRead)
def delete_role_permission(role_permission_id: UUID, db: Session = Depends(get_db)):
    role_perm = role_permission_crud.delete(db, role_permission_id)
    if not role_perm:
        raise HTTPException(status_code=404, detail="RolePermission not found")
    return role_perm
