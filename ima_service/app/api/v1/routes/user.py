"""User-related API routes with standardized APIResponse."""

from typing import List
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
    summary="Create a new user",
    description="Create a new user in the system and automatically assign them the default `VIEWER` role.",
)
async def create_user_endpoint(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    - Creates a new user.
    - Assigns default VIEWER role.
    - Returns the created user details.
    """
    # Check if user with the same email already exists
    existing_user = await crud_user.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user_in.email}' already exists.",
        )

    # Create the user
    db_user = await crud_user.create_user(db, user_in)

    # Assign default VIEWER role
    viewer_role = await crud_role.get_role_by_name(db, RoleName.VIEWER)
    if viewer_role:
        await assign_role_to_user(db, db_user, viewer_role)

    # Refresh to get updated info from DB
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
    summary="Assign a ROLE to a USER",
    description=(
        "Assign or update a single role for a user within an optional tenant.\n\n"
        "- `user_id`: **UUID** of the user.\n"
        "- `role_name`: **Role** to assign (use one of the predefined roles).\n"
        "- `tenant_id`: Optional **tenant ID** for multi-tenant role assignment.\n"
        "- Returns **404** if the user or role does not exist.\n"
        "- Returns the assigned `ROLE` details on success."
    ),
)
async def assign_role_to_user_endpoint(
    user_id: UUID,
    role_name: RoleName = Query(
        ..., description="Select a single role to assign", example=RoleName.TENANT_ADMIN
    ),
    tenant_id: UUID | None = Query(
        None, description="Optional tenant ID for multi-tenant role assignment"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Assign or update a role for a user, optionally scoped to a tenant.
    """
    # Fetch user
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found.",
        )

    # Fetch role
    role = await crud_role.get_role_by_name(db, role_name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name.value}' not found.",
        )

    # Check for existing role in the same tenant
    existing_role = next(
        (r for r in user.roles if getattr(r, "tenant_id", None) == tenant_id), None
    )

    # Assign or update role
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
    summary="List users with pagination",
    description="Retrieve a paginated list of `USER` including full pagination metadata.",
)
async def list_users_endpoint(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of records to return"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    - Returns paginated users.
    - Includes `previousPage`, `nextPage`, `firstPage`, `lastPage` URLs.
    - Supports `skip` and `limit` query parameters.
    """
    # Fetch total count and users for pagination
    total, users = await crud_user.list_users(db, skip=skip, limit=limit)
    user_schemas = [crud_user.user_to_schema(u) for u in users]

    last_skip = ((total - 1) // limit) * limit if total > 0 else 0

    # Helper to build pagination URLs
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
    summary="Retrieve a USER by ID",
    description="Fetch a single `USER` by their **UUID**. Returns **404** if the `USER` does not exist.",
)
async def get_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    - `user_id`: UUID of the user to retrieve.
    - Returns user details in standardized response.
    - Raises 404 if user not found.
    """
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found.",
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
    summary="Update a USER by ID",
    description=(
        "Update a user's information including email, password, or active status.\n\n"
        "- `user_id`: **UUID** of the user to update.\n"
        "- Returns **404** if the user does not exist.\n"
        "- Returns the updated `USER` in standardized response format."
    ),
)
async def update_user_endpoint(
    user_id: UUID, user_in: UserUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update a user's email, password, or superuser status.
    """
    # Fetch the user
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found.",
        )

    # Update the user
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
    summary="Deactivate a USER by ID",
    description=(
        "Deactivate a user account by their **UUID**.\n\n"
        "- `user_id`: **UUID** of the user to deactivate.\n"
        "- Returns **404** if the user does not exist.\n"
        "- Returns the deactivated `USERS`'s details."
    ),
)
async def deactivate_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Deactivate a user account.
    """
    user = await crud_user.deactivate_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found.",
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
    summary="Reactivate a USER by ID",
    description=(
        "Reactivate a previously deactivated user account by their UUID.\n\n"
        "- `user_id`:**UUID** of the user to reactivate.\n"
        "- Returns **404** if the user does not exist.\n"
        "- Returns the reactivated `USER`'s details."
    ),
)
async def reactivate_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Reactivate a deactivated user account.
    """
    user = await crud_user.reactivate_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found.",
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
    summary="Delete a USER by ID",
    description=(
        "Permanently delete a user account by their UUID.\n\n"
        "- `user_id`: **UUID** of the user to delete.\n"
        "- Returns **404** if the user does not exist.\n"
        "- Returns **204** No Content on successful deletion."
    ),
)
async def delete_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Permanently delete a user account.
    """
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID '{user_id}' not found.",
        )

    await db.delete(user)
    await db.commit()
    return None
