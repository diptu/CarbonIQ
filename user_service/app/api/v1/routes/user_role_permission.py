"""API routes for managing user-role-permission assignments."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from user_service.app.crud.user_role_permission import user_role_permission_crud
from user_service.app.db.session import get_db
from user_service.app.schemas.user_role_permission import (
    UserRolePermissionCreate,
    UserRolePermissionRead,
    UserRolePermissionUpdate,
)

router = APIRouter(prefix="/user-role-permissions", tags=["user_role_permissions"])


@router.post("/", response_model=UserRolePermissionRead, status_code=status.HTTP_201_CREATED)
def assign_user_role_permission(
    urp_in: UserRolePermissionCreate, db: Session = Depends(get_db)
) -> UserRolePermissionRead:
    """
    Assign a role and permission to a user.

    Args:
        urp_in: UserRolePermissionCreate schema containing user_id, role_id, permission_id.
        db: SQLAlchemy DB session.

    Returns:
        The created UserRolePermissionRead object.
    """
    urp = user_role_permission_crud.create(db, urp_in)
    return UserRolePermissionRead.model_validate(urp)


@router.get("/", response_model=List[UserRolePermissionRead])
def list_user_role_permissions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[UserRolePermissionRead]:
    """
    Retrieve paginated list of user-role-permission assignments.

    Args:
        skip: Records to skip.
        limit: Max records to return.
        db: SQLAlchemy DB session.

    Returns:
        List of UserRolePermissionRead objects.
    """
    urp_list = user_role_permission_crud.get_all(db, skip=skip, limit=limit)
    return [UserRolePermissionRead.model_validate(item) for item in urp_list]


@router.delete("/{urp_id}", response_model=UserRolePermissionRead)
def delete_user_role_permission(
    urp_id: UUID, db: Session = Depends(get_db)
) -> UserRolePermissionRead:
    """
    Delete a user-role-permission assignment by its ID.

    Args:
        urp_id: UUID of the assignment.
        db: SQLAlchemy DB session.

    Returns:
        Deleted UserRolePermissionRead object.

    Raises:
        HTTPException: If no matching record is found.
    """
    urp = user_role_permission_crud.delete(db, urp_id)
    if not urp:
        raise HTTPException(status_code=404, detail="User-Role-Permission mapping not found")
    return UserRolePermissionRead.model_validate(urp)


@router.put("/{urp_id}", response_model=UserRolePermissionRead)
def update_user_role_permission(
    urp_id: UUID,
    urp_in: UserRolePermissionUpdate,
    db: Session = Depends(get_db),
) -> UserRolePermissionRead:
    """
    Update the user, role, or permission referenced in the assignment.

    Prevents duplicates — if an identical mapping already exists,
    it returns HTTP 400.
    """
    existing = user_role_permission_crud.get(db, urp_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Check for duplicate (new user-role-permission combo already exists)
    duplicate = user_role_permission_crud.get_by_user_role_permission(
        db, urp_in.user_id, urp_in.role_id, urp_in.permission_id
    )
    if duplicate and duplicate.id != urp_id:
        raise HTTPException(
            status_code=400,
            detail="An identical user-role-permission assignment already exists",
        )

    updated = user_role_permission_crud.update(db, existing, urp_in)
    return UserRolePermissionRead.model_validate(updated)
