"""User-related API routes."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.crud import user_basic as crud_user
from app.crud import role as crud_role
from app.crud.user_roles import assign_role_to_user
from app.schemas.user import UserRead, UserCreate, UserListResponse
from app.schemas.role import RoleRead, RoleName

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead)
async def create_user_endpoint(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user and assign default VIEWER role."""
    db_user = await crud_user.create_user(db, user_in)

    viewer_role = await crud_role.get_role_by_name(db, RoleName.VIEWER)
    if viewer_role:
        await assign_role_to_user(db, db_user, viewer_role)

    await db.refresh(db_user)
    return UserRead(
        id=db_user.id,
        email=db_user.email,
        is_active=db_user.is_active,
        is_superuser=db_user.is_superuser,
        roles=[RoleRead.from_orm(r) for r in db_user.roles],
    )


@router.post("/{user_id}/roles", response_model=RoleRead)
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

    # Check if user already has a role in this tenant
    existing_role = None
    for r in user.roles:
        if getattr(r, "tenant_id", None) == tenant_id:
            existing_role = r
            break

    if existing_role:
        # Update the role for the tenant
        await crud_user.update_user_role(db, user, existing_role, role, tenant_id)
    else:
        # Assign new role
        await assign_role_to_user(db, user, role, tenant_id=tenant_id)

    await db.commit()
    await db.refresh(user)

    return RoleRead.from_orm(role)


# @router.post("/{user_id}/roles", response_model=RoleRead)
# async def assign_role_to_user_endpoint(
#     user_id: UUID,
#     role_name: RoleName = Query(
#         ..., description="Select a single role to assign", example=RoleName.TENANT_ADMIN
#     ),
#     db: AsyncSession = Depends(get_db),
# ):
#     """Assign or update a single role for a user."""
#     user = await crud_user.get_user(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     role = await crud_role.get_role_by_name(db, role_name)
#     if not role:
#         raise HTTPException(
#             status_code=404, detail=f"Role '{role_name.value}' not found"
#         )

#     if user.roles:
#         user.roles[0] = role
#     else:
#         await assign_role_to_user(db, user, role)

#     await db.commit()
#     await db.refresh(user)

#     return RoleRead.from_orm(role)


@router.get("/", response_model=UserListResponse)
async def list_users_endpoint(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List users with pagination metadata."""
    total, users = await crud_user.list_users(db, skip=skip, limit=limit)

    def build_url(skip_value: int) -> str | None:
        if 0 <= skip_value < total:
            return str(request.url.replace_query_params(skip=skip_value, limit=limit))
        return None

    previous_page = build_url(skip - limit)
    next_page = build_url(skip + limit)
    first_page = build_url(0)
    last_skip = ((total - 1) // limit) * limit
    last_page = build_url(last_skip)

    return UserListResponse(
        total=total,
        previousPage=previous_page,
        nextPage=next_page,
        firstPage=first_page,
        lastPage=last_page,
        users=users,
    )


@router.get("/{user_id}", response_model=UserRead)
async def get_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a user by ID."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserRead(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=[RoleRead.from_orm(r) for r in user.roles],
    )


@router.put("/{user_id}", response_model=UserRead)
async def update_user_endpoint(
    user_id: UUID, user_in: UserCreate, db: AsyncSession = Depends(get_db)
):
    """Update a user's email, password, or superuser status."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await crud_user.update_user(db, user, user_in)
    await db.refresh(updated_user)

    return UserRead(
        id=updated_user.id,
        email=updated_user.email,
        is_active=updated_user.is_active,
        is_superuser=updated_user.is_superuser,
        roles=[RoleRead.from_orm(r) for r in updated_user.roles],
    )


@router.post("/{user_id}/deactivate", response_model=UserRead)
async def deactivate_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Deactivate a user."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()
    await db.refresh(user)

    return UserRead(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=[RoleRead.from_orm(r) for r in user.roles],
    )


@router.post("/{user_id}/reactivate", response_model=UserRead)
async def reactivate_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Reactivate a user."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = True
    await db.commit()
    await db.refresh(user)

    return UserRead(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        roles=[RoleRead.from_orm(r) for r in user.roles],
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(user_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a user by ID."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Use AsyncSession delete
    await db.delete(user)
    await db.commit()

    return None  # 204 No Content
