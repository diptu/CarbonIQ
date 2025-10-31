"""API routes for managing user permissions."""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.user_permission import user_permission_crud
from app.db.session import get_db
from app.schemas.user_permission import UserPermissionRead

router = APIRouter(prefix="/user-permissions", tags=["user_permissions"])


# @router.post("/", response_model=UserPermissionRead, status_code=status.HTTP_201_CREATED)
# def assign_permission(
#     user_perm_in: UserPermissionCreate, db: Session = Depends(get_db)
# ) -> UserPermissionRead:
#     """
#     Assign a permission to a user.

#     Args:
#         user_perm_in: UserPermissionCreate schema containing user and permission details.
#         db: SQLAlchemy database session.

#     Returns:
#         The created UserPermissionRead object.
#     """
#     user_perm = user_permission_crud.create(db, user_perm_in)
#     return UserPermissionRead.model_validate(user_perm)  # Pydantic v2


@router.get("/", response_model=List[UserPermissionRead])
def list_user_permissions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[UserPermissionRead]:
    """
    Retrieve a paginated list of user-permission assignments.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: SQLAlchemy database session.

    Returns:
        List of UserPermissionRead objects.
    """
    user_perms = user_permission_crud.get_all(db, skip=skip, limit=limit)
    return [UserPermissionRead.model_validate(up) for up in user_perms]  # Pydantic v2


# @router.delete("/{user_permission_id}", response_model=UserPermissionRead)
# def delete_user_permission(
#     user_permission_id: UUID, db: Session = Depends(get_db)
# ) -> UserPermissionRead:
#     """
#     Delete a user-permission assignment by its UUID.

#     Args:
#         user_permission_id: UUID of the user-permission assignment.
#         db: SQLAlchemy database session.

#     Returns:
#         The deleted UserPermissionRead object.

#     Raises:
#         HTTPException: If the user-permission assignment is not found.
#     """
#     user_perm = user_permission_crud.delete(db, user_permission_id)
#     if not user_perm:
#         raise HTTPException(status_code=404, detail="UserPermission not found")
#     return UserPermissionRead.model_validate(user_perm)  # Pydantic v2
