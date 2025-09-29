"""User-related API routes with standardized APIResponse."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import create_model

from app.api.deps import get_db
from app.crud import user_basic as crud_user
from app.crud import role as crud_role
from app.crud.user_roles import assign_role_to_user
from app.schemas.user import UserRead, UserCreate, UserUpdate, UserList
from app.schemas.base import APIResponse
from app.schemas.role import RoleRead, RoleName

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
@router.post("/", response_model=UserReadResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user and assign default VIEWER role."""
    db_user = await crud_user.create_user(db, user_in)

    viewer_role = await crud_role.get_role_by_name(db, RoleName.VIEWER)
    if viewer_role:
        await assign_role_to_user(db, db_user, viewer_role)

    await db.refresh(db_user)

    return UserReadResponse(
        statusCode=201,
        msg="User created successfully",
        details=crud_user.user_to_schema(db_user),
    )


# ----------------------
# Assign Role
# ----------------------
@router.post("/{user_id}/roles", response_model=RoleReadResponse)
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
    """Assign or update a single role for a user within an optional tenant."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = await crud_role.get_role_by_name(db, role_name)
    if not role:
        raise HTTPException(
            status_code=404, detail=f"Role '{role_name.value}' not found"
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
        statusCode=200,
        msg="Role assigned successfully",
        details=RoleRead.from_orm(role),
    )


# ----------------------
# List Users
# ----------------------
@router.get("/", response_model=UserListResponse)
async def list_users_endpoint(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List users with full pagination metadata and standardized response."""
    total, users = await crud_user.list_users(db, skip=skip, limit=limit)
    user_schemas = [crud_user.user_to_schema(u) for u in users]

    last_skip = ((total - 1) // limit) * limit

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
        statusCode=200,
        msg="Users retrieved successfully",
        details=paginated,
    )


# ----------------------
# Get User by ID
# ----------------------
@router.get("/{user_id}", response_model=UserReadResponse)
async def get_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a user by ID."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserReadResponse(
        statusCode=200,
        msg="User retrieved successfully",
        details=crud_user.user_to_schema(user),
    )


# ----------------------
# Update User
# ----------------------
@router.put("/{user_id}", response_model=UserReadResponse)
async def update_user_endpoint(
    user_id: UUID, user_in: UserUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a user's email, password, or superuser status."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await crud_user.update_user(db, user, user_in)
    await db.refresh(updated_user)

    return UserReadResponse(
        statusCode=200,
        msg="User updated successfully",
        details=crud_user.user_to_schema(updated_user),
    )


# ----------------------
# Deactivate User
# ----------------------
@router.post("/{user_id}/deactivate", response_model=UserReadResponse)
async def deactivate_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await crud_user.deactivate_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserReadResponse(
        statusCode=200,
        msg="User deactivated successfully",
        details=crud_user.user_to_schema(user),
    )


# ----------------------
# Reactivate User
# ----------------------
@router.post("/{user_id}/reactivate", response_model=UserReadResponse)
async def reactivate_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    user = await crud_user.reactivate_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserReadResponse(
        statusCode=200,
        msg="User reactivated successfully",
        details=crud_user.user_to_schema(user),
    )


# ----------------------
# Delete User
# ----------------------
@router.delete(
    "/{user_id}", response_model=None, status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a user by ID."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await db.delete(user)
    await db.commit()
    return None
