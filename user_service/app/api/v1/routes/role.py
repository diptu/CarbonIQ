"""API routes for managing roles."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from shared_service.app.core.deps import require_permissions
from sqlalchemy.orm import Session

from user_service.app.crud.role import role_crud
from user_service.app.db.session import get_db
from user_service.app.schemas.role import RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post(
    "/",
    response_model=RoleOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(permissions=["role.create"]))],
)
def create_role(role_in: RoleCreate, db: Session = Depends(get_db)) -> RoleOut:
    """
    Create a new role if it does not already exist.

    Args:
        role_in: RoleCreate schema containing role details.
        db: SQLAlchemy database session.

    Returns:
        The created RoleOut object.

    Raises:
        HTTPException: If a role with the same name already exists.
    """
    db_role = role_crud.get_by_name(db, role_in.name)
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    role = role_crud.create(db, role_in)
    return RoleOut.model_validate(role)


@router.get("/{role_id}", response_model=RoleOut)
def get_role(role_id: UUID, db: Session = Depends(get_db)) -> RoleOut:
    """
    Retrieve a role by its UUID.

    Args:
        role_id: UUID of the role.
        db: SQLAlchemy database session.

    Returns:
        The requested RoleOut object.

    Raises:
        HTTPException: If the role is not found.
    """
    role = role_crud.get(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return RoleOut.model_validate(role)


@router.get("/", response_model=List[RoleOut])
def list_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[RoleOut]:
    """
    Retrieve a paginated list of roles.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session.

    Returns:
        List of RoleOut objects.
    """
    roles = role_crud.get_all(db, skip=skip, limit=limit)
    return [RoleOut.model_validate(r) for r in roles]


@router.put("/{role_id}", response_model=RoleOut)
def update_role(role_id: UUID, role_in: RoleUpdate, db: Session = Depends(get_db)) -> RoleOut:
    """
    Update an existing role.

    Args:
        role_id: UUID of the role to update.
        role_in: RoleUpdate schema containing updated fields.
        db: SQLAlchemy database session.

    Returns:
        The updated RoleOut object.

    Raises:
        HTTPException: If the role is not found.
    """
    role = role_crud.get(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    updated_role = role_crud.update(db, role, role_in)
    return RoleOut.model_validate(updated_role)


@router.delete("/{role_id}", response_model=RoleOut)
def delete_role(role_id: UUID, db: Session = Depends(get_db)) -> RoleOut:
    """
    Delete a role by its UUID.

    Args:
        role_id: UUID of the role to delete.
        db: SQLAlchemy database session.

    Returns:
        The deleted RoleOut object.

    Raises:
        HTTPException: If the role is not found.
    """
    role = role_crud.delete(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return RoleOut.model_validate(role)
