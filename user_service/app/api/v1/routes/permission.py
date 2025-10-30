from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.permission import permission_crud
from app.db.session import get_db
from app.schemas.permission import PermissionCreate, PermissionOut, PermissionUpdate

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.post("/", response_model=PermissionOut, status_code=status.HTTP_201_CREATED)
def create_permission(permission_in: PermissionCreate, db: Session = Depends(get_db)):
    db_perm = permission_crud.get_by_name(db, permission_in.name)
    if db_perm:
        raise HTTPException(status_code=400, detail="Permission already exists")
    return permission_crud.create(db, permission_in)


@router.get("/{permission_id}", response_model=PermissionOut)
def get_permission(permission_id: UUID, db: Session = Depends(get_db)):
    perm = permission_crud.get(db, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    return perm


@router.get("/", response_model=list[PermissionOut])
def list_permissions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return permission_crud.get_all(db, skip=skip, limit=limit)


@router.put("/{permission_id}", response_model=PermissionOut)
def update_permission(
    permission_id: UUID, permission_in: PermissionUpdate, db: Session = Depends(get_db)
):
    perm = permission_crud.get(db, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    return permission_crud.update(db, perm, permission_in)


@router.delete("/{permission_id}", response_model=PermissionOut)
def delete_permission(permission_id: UUID, db: Session = Depends(get_db)):
    perm = permission_crud.delete(db, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    return perm
