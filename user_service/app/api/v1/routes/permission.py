"""API routes for managing permissions."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from user_service.app.crud.permission import permission_crud
from user_service.app.db.session import get_db
from user_service.app.schemas.permission import PermissionCreate, PermissionOut, PermissionUpdate

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.post("/", response_model=PermissionOut, status_code=status.HTTP_201_CREATED)
def create_permission(
    permission_in: PermissionCreate, db: Session = Depends(get_db)
) -> PermissionOut:
    """
    Create a new permission if it does not already exist.

    Args:
        permission_in: PermissionCreate schema containing permission details.
        db: SQLAlchemy database session.

    Returns:
        The created PermissionOut object.

    Raises:
        HTTPException: If a permission with the same name already exists.
    """
    db_perm = permission_crud.get_by_name(db, permission_in.name)
    if db_perm:
        raise HTTPException(status_code=400, detail="Permission already exists")

    perm = permission_crud.create(db, permission_in)
    return PermissionOut.model_validate(perm)


@router.get("/{permission_id}", response_model=PermissionOut)
def get_permission(permission_id: UUID, db: Session = Depends(get_db)) -> PermissionOut:
    """
    Retrieve a permission by its UUID.

    Args:
        permission_id: UUID of the permission.
        db: SQLAlchemy database session.

    Returns:
        The requested PermissionOut object.

    Raises:
        HTTPException: If the permission is not found.
    """
    perm = permission_crud.get(db, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    return PermissionOut.model_validate(perm)


@router.get("/", response_model=List[PermissionOut])
def list_permissions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[PermissionOut]:
    """
    Retrieve a paginated list of permissions.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session.

    Returns:
        List of PermissionOut objects.
    """
    perms = permission_crud.get_all(db, skip=skip, limit=limit)
    return [PermissionOut.model_validate(p) for p in perms]


@router.put("/{permission_id}", response_model=PermissionOut)
def update_permission(
    permission_id: UUID, permission_in: PermissionUpdate, db: Session = Depends(get_db)
) -> PermissionOut:
    """
    Update an existing permission.

    Args:
        permission_id: UUID of the permission to update.
        permission_in: PermissionUpdate schema containing updated fields.
        db: SQLAlchemy database session.

    Returns:
        The updated PermissionOut object.

    Raises:
        HTTPException: If the permission is not found.
    """
    perm = permission_crud.get(db, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    updated_perm = permission_crud.update(db, perm, permission_in)
    return PermissionOut.model_validate(updated_perm)


@router.delete("/{permission_id}", response_model=PermissionOut)
def delete_permission(permission_id: UUID, db: Session = Depends(get_db)) -> PermissionOut:
    """
    Delete a permission by its UUID.

    Args:
        permission_id: UUID of the permission to delete.
        db: SQLAlchemy database session.

    Returns:
        The deleted PermissionOut object.

    Raises:
        HTTPException: If the permission is not found.
    """
    perm = permission_crud.delete(db, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")
    return PermissionOut.model_validate(perm)
