"""User-related API routes with standardized APIResponse."""

from uuid import UUID

from app.api.deps import get_db
from app.crud import role as crud_role
from app.crud import user_basic as crud_user
from app.crud.user_roles import assign_role_to_user
from app.schemas.base import APIResponse
from app.schemas.role import RoleName, RoleRead
from app.schemas.user import UserCreate, UserList, UserRead, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from ima_service.app.api.v1.docs.user_docs import (
    ASSIGN_ROLE,
    CREATE_USER,
    DEACTIVATE_USER,
    DELETE_USER,
    GET_USER_BY_ID,
    LIST_USERS,
    REACTIVATE_USER,
    UPDATE_USER,
)

router = APIRouter(prefix="/users", tags=["users"])

# ----------------------
# Concrete response models for OpenAPI
# ----------------------
UserReadResponse = create_model(
    "UserReadResponse", __base__=APIResponse, details=(UserRead, ...)
)

UserListResponse = create_model(
    "UserListResponse", __base__=APIResponse, details=(UserList, ...)
)

RoleReadResponse = create_model(
    "RoleReadResponse", __base__=APIResponse, details=(RoleRead, ...)
)


# ----------------------
# Create User
# ----------------------
@router.post(
    "/",
    response_model=UserReadResponse,
    status_code=status.HTTP_201_CREATED,
    summary=CREATE_USER["summary"],
    description=CREATE_USER["description"],
)
async def create_user_endpoint(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user and assign the default VIEWER role.

    Parameters
    ----------
    user_in : UserCreate
        Pydantic model containing user creation details.
    db : AsyncSession, optional
        SQLAlchemy async session.

    Returns
    -------
    UserReadResponse
        Standardized response containing user details and assigned roles.

    Raises
    ------
    HTTPException
        If a user with the same email already exists (400).
    """
    existing_user = await crud_user.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user_in.email}' already exists.",
        )

    db_user = await crud_user.create_user(db, user_in)
    viewer_role = await crud_role.get_role_by_name(db, RoleName.VIEWER)
    if viewer_role:
        await assign_role_to_user(db, db_user, viewer_role)

    await db.refresh(db_user)
    return UserReadResponse(
        statusCode=status.HTTP_201_CREATED,
        msg="User created successfully",
        details=crud_user.user_to_schema(db_user),
    )


# ----------------------
# Assign Role
# ----------------------
@router.post(
    "/{user_id}/roles",
    response_model=RoleReadResponse,
    status_code=status.HTTP_200_OK,
    summary=ASSIGN_ROLE["summary"],
    description=ASSIGN_ROLE["description"],
)
async def assign_role_to_user_endpoint(
    user_id: UUID,
    role_name: RoleName = Query(
        ..., description="Select a role", example=RoleName.TENANT_ADMIN
    ),
    tenant_id: UUID | None = Query(None, description="Optional tenant ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Assign or update a role for a user, optionally scoped to a tenant.

    Parameters
    ----------
    user_id : UUID
        The ID of the user.
    role_name : RoleName
        The role to assign.
    tenant_id : UUID, optional
        Optional tenant ID for multi-tenant assignments.
    db : AsyncSession, optional
        SQLAlchemy async session.

    Returns
    -------
    RoleReadResponse
        Standardized response with assigned role details.

    Raises
    ------
    HTTPException
        If user or role does not exist (404).
    """
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found."
        )

    role = await crud_role.get_role_by_name(db, role_name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name.value}' not found.",
        )

    existing_role = next(
        (r for r in user.roles if getattr(r, "tenant_id", None) == tenant_id), None
    )
    if existing_role:
        await crud_user.update_user_role(db, user, existing_role, role, tenant_id)
    else:
        await assign_role_to_user(db, user, role, tenant_id=tenant_id)

    await db.commit()
    await db.refresh(user)

    return RoleReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="Role assigned successfully",
        details=RoleRead.from_orm(role),
    )


# ----------------------
# List Users
# ----------------------
@router.get(
    "/",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary=LIST_USERS["summary"],
    description=LIST_USERS["description"],
)
async def list_users_endpoint(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a paginated list of users.

    Parameters
    ----------
    request : Request
        FastAPI request object (for pagination URLs).
    skip : int
        Number of records to skip.
    limit : int
        Maximum number of records to return.
    db : AsyncSession, optional
        SQLAlchemy async session.

    Returns
    -------
    UserListResponse
        Paginated users with previous/next/first/last page URLs.
    """
    total, users = await crud_user.list_users(db, skip=skip, limit=limit)
    user_schemas = [crud_user.user_to_schema(u) for u in users]

    last_skip = ((total - 1) // limit) * limit if total > 0 else 0

    def build_url(skip_value: int) -> str | None:
        if 0 <= skip_value < total:
            return str(request.url.replace_query_params(skip=skip_value, limit=limit))
        return None

    paginated = UserList(
        total=total,
        skip=skip,
        limit=limit,
        previousPage=build_url(skip - limit),
        nextPage=build_url(skip + limit),
        firstPage=build_url(0),
        lastPage=build_url(last_skip),
        items=user_schemas,
    )

    return UserListResponse(
        statusCode=status.HTTP_200_OK,
        msg="Users retrieved successfully",
        details=paginated,
    )


# ----------------------
# Get User by ID
# ----------------------
@router.get(
    "/{user_id}",
    response_model=UserReadResponse,
    status_code=status.HTTP_200_OK,
    summary=GET_USER_BY_ID["summary"],
    description=GET_USER_BY_ID["description"],
)
async def get_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a single user by their unique ID (UUID).

    Parameters
    ----------
    user_id : UUID
        The unique identifier of the user to fetch.
    db : AsyncSession, optional
        SQLAlchemy async session.

    Returns
    -------
    UserReadResponse
        Standardized API response containing user details and roles.

    Raises
    ------
    HTTPException
        If the user does not exist (404).
    """
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found.",
        )

    return UserReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="User retrieved successfully",
        details=crud_user.user_to_schema(user),
    )


# ----------------------
# Update User
# ----------------------
@router.put(
    "/{user_id}",
    response_model=UserReadResponse,
    status_code=status.HTTP_200_OK,
    summary=UPDATE_USER["summary"],
    description=UPDATE_USER["description"],
)
async def update_user_endpoint(
    user_id: UUID, user_in: UserUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update a user's information.

    Parameters
    ----------
    user_id : UUID
        ID of the user to update.
    user_in : UserUpdate
        Data to update (email, password, active status, etc.).
    db : AsyncSession, optional
        SQLAlchemy async session.

    Returns
    -------
    UserReadResponse
        Updated user details in standardized format.

    Raises
    ------
    HTTPException
        If user does not exist (404).
    """
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found."
        )
    updated_user = await crud_user.update_user(db, user, user_in)
    await db.refresh(updated_user)
    return UserReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="User updated successfully",
        details=crud_user.user_to_schema(updated_user),
    )


# ----------------------
# Deactivate User
# ----------------------
@router.post(
    "/{user_id}/deactivate",
    response_model=UserReadResponse,
    status_code=status.HTTP_200_OK,
    summary=DEACTIVATE_USER["summary"],
    description=DEACTIVATE_USER["description"],
)
async def deactivate_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Deactivate a user account temporarily.

    Parameters
    ----------
    user_id : UUID
        ID of the user to deactivate.
    db : AsyncSession, optional
        SQLAlchemy async session.

    Returns
    -------
    UserReadResponse
        Standardized response with user details.

    Raises
    ------
    HTTPException
        If user does not exist (404).
    """
    user = await crud_user.deactivate_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found."
        )
    return UserReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="User deactivated successfully",
        details=crud_user.user_to_schema(user),
    )


# ----------------------
# Reactivate User
# ----------------------
@router.post(
    "/{user_id}/reactivate",
    response_model=UserReadResponse,
    status_code=status.HTTP_200_OK,
    summary=REACTIVATE_USER["summary"],
    description=REACTIVATE_USER["description"],
)
async def reactivate_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Reactivate a previously deactivated user account.

    Parameters
    ----------
    user_id : UUID
        ID of the user to reactivate.
    db : AsyncSession, optional
        SQLAlchemy async session.

    Returns
    -------
    UserReadResponse
        Standardized response with user details.

    Raises
    ------
    HTTPException
        If user does not exist (404).
    """
    user = await crud_user.reactivate_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found."
        )
    return UserReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="User reactivated successfully",
        details=crud_user.user_to_schema(user),
    )


# ----------------------
# Delete User
# ----------------------
@router.delete(
    "/{user_id}",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    summary=DELETE_USER["summary"],
    description=DELETE_USER["description"],
)
async def delete_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Permanently delete a user account.

    Parameters
    ----------
    user_id : UUID
        ID of the user to delete.
    db : AsyncSession, optional
        SQLAlchemy async session.

    Returns
    -------
    None

    Raises
    ------
    HTTPException
        If user does not exist (404).
    """
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found."
        )
    await db.delete(user)
    await db.commit()
    return None
