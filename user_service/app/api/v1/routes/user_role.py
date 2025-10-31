"""API routes for managing user roles."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud.user_role import user_role_crud
from app.db.session import get_db
from app.schemas.user_role import UserRoleCreate, UserRoleOut

router = APIRouter(prefix="/user-roles", tags=["user_roles"])


@router.post("/", response_model=UserRoleOut, status_code=status.HTTP_201_CREATED)
def assign_role(user_role_in: UserRoleCreate, db: Session = Depends(get_db)) -> UserRoleOut:
    """
    Assign a role to a user.

    Args:
        user_role_in: UserRoleCreate schema containing user and role details.
        db: SQLAlchemy database session.

    Returns:
        The created UserRoleOut object.
    """
    user_role = user_role_crud.create(db, user_role_in)
    return UserRoleOut.model_validate(user_role)  # Pydantic v2


@router.get("/", response_model=List[UserRoleOut])
def list_user_roles(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[UserRoleOut]:
    """
    Retrieve a paginated list of user-role assignments.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session.

    Returns:
        List of UserRoleOut objects.
    """
    user_roles = user_role_crud.get_all(db, skip=skip, limit=limit)
    return [UserRoleOut.model_validate(ur) for ur in user_roles]  # Pydantic v2


@router.delete("/{user_role_id}", response_model=UserRoleOut)
def delete_user_role(user_role_id: UUID, db: Session = Depends(get_db)) -> UserRoleOut:
    """
    Delete a user-role assignment by its UUID.

    Args:
        user_role_id: UUID of the user-role assignment.
        db: SQLAlchemy database session.

    Returns:
        The deleted UserRoleOut object.

    Raises:
        HTTPException: If the user-role assignment is not found.
    """
    user_role = user_role_crud.delete(db, user_role_id)
    if not user_role:
        raise HTTPException(status_code=404, detail="UserRole not found")
    return UserRoleOut.model_validate(user_role)  # Pydantic v2
