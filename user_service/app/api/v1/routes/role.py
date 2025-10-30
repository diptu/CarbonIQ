from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_roles_permissions
from app.crud.role import role_crud
from app.db.session import get_db
from app.schemas.role import RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post(
    "/",
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles_permissions(roles=["admin"], permissions=["role.create"]))],
)
def create_role(role_in: RoleCreate, db: Session = Depends(get_db)):
    db_role = role_crud.get_by_name(db, role_in.name)
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    return role_crud.create(db, role_in)


@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: UUID, db: Session = Depends(get_db)):
    role = role_crud.get(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role


@router.get("/", response_model=list[RoleOut])
def list_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return role_crud.get_all(db, skip=skip, limit=limit)


@router.put("/{role_id}", response_model=RoleOut)
def update_role(role_id: UUID, role_in: RoleUpdate, db: Session = Depends(get_db)):
    role = role_crud.get(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role_crud.update(db, role, role_in)


@router.delete("/{role_id}", response_model=RoleOut)
def delete_role(role_id: UUID, db: Session = Depends(get_db)):
    role = role_crud.delete(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role
