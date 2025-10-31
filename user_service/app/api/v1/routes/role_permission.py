"""API routes for managing role-permission assignments."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.role_permission import role_permission_crud
from app.db.session import get_db
from app.schemas.role_permission import RolePermissionCreate, RolePermissionRead

router = APIRouter(prefix="/role-permissions", tags=["role_permissions"])


@router.post("/", response_model=RolePermissionRead, status_code=status.HTTP_201_CREATED)
def assign_permission_to_role(
    role_perm_in: RolePermissionCreate, db: Session = Depends(get_db)
) -> RolePermissionRead:
    """
    Assign a permission to a role.

    Args:
        role_perm_in: RolePermissionCreate schema containing role and permission details.
        db: SQLAlchemy database session.

    Returns:
        The created RolePermissionRead object.
    """
    role_perm = role_permission_crud.create(db, role_perm_in)
    return RolePermissionRead.model_validate(role_perm)  # Pydantic v2


@router.get("/", response_model=List[RolePermissionRead])
def list_role_permissions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[RolePermissionRead]:
    """
    Retrieve a paginated list of role-permission assignments.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session.

    Returns:
        List of RolePermissionRead objects.
    """
    role_perms = role_permission_crud.get_all(db, skip=skip, limit=limit)
    return [RolePermissionRead.model_validate(rp) for rp in role_perms]  # Pydantic v2


@router.delete("/{role_permission_id}", response_model=RolePermissionRead)
def delete_role_permission(
    role_permission_id: UUID, db: Session = Depends(get_db)
) -> RolePermissionRead:
    """
    Delete a role-permission assignment by its UUID.

    Args:
        role_permission_id: UUID of the role-permission assignment.
        db: SQLAlchemy database session.

    Returns:
        The deleted RolePermissionRead object.

    Raises:
        HTTPException: If the role-permission assignment is not found.
    """
    role_perm = role_permission_crud.delete(db, role_permission_id)
    if not role_perm:
        raise HTTPException(status_code=404, detail="RolePermission not found")
    return RolePermissionRead.model_validate(role_perm)  # Pydantic v2
