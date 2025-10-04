# app/api/v1/routes/users.py
"""User-related API routes with standardized APIResponse, RBAC enforcement, and audit logging."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ima_service.app.api.deps import get_db, require_roles, get_current_active_user
from ima_service.app.crud import role as crud_role
from ima_service.app.crud import user_basic as crud_user
from ima_service.app.crud.user_roles import assign_role_to_user
from ima_service.app.schemas.base import APIResponse
from ima_service.app.schemas.role import RoleName, RoleRead
from ima_service.app.schemas.user import UserCreate, UserList, UserRead, UserUpdate
from ima_service.app.utils.audit import log_audit_event
from ima_service.app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

# ----------------------
# Response models
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
# Utility: get tenant_id for a user
# ----------------------
async def _get_tenant_id(db: AsyncSession, user_id: UUID) -> str | None:
    result = await db.execute(
        text("SELECT tenant_id FROM user_roles WHERE user_id = :uid LIMIT 1"),
        {"uid": str(user_id)},
    )
    row = result.first()
    return str(row[0]) if row else None


# ----------------------
# Create User
# ----------------------
@router.post("/", response_model=UserReadResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_in: UserCreate,
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("MEMBER")),
):
    existing_user = await crud_user.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="User already exists")

    db_user = await crud_user.create_user(db, user_in)
    viewer_role = await crud_role.get_role_by_name(db, RoleName.VIEWER)
    if viewer_role:
        await assign_role_to_user(db, db_user, viewer_role, tenant_id)

    log_audit_event(
        actor_id=str(current_user.id),
        target_id=str(db_user.id),
        action="create_user",
        role=RoleName.VIEWER.value if viewer_role else None,
        tenant_id=str(tenant_id),
    )

    return UserReadResponse(
        statusCode=status.HTTP_201_CREATED,
        msg="User created successfully",
        details=crud_user.user_to_schema(db_user),
    )


# ----------------------
# List Users
# ----------------------
@router.get("/", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def list_users_endpoint(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("MEMBER")),
):
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
@router.get("/{user_id}", response_model=UserReadResponse)
async def get_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("MEMBER")),
):
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="User retrieved successfully",
        details=crud_user.user_to_schema(user),
    )


# ----------------------
# Assign Role
# ----------------------
@router.post("/{user_id}/roles", response_model=RoleReadResponse)
async def assign_role_endpoint(
    user_id: UUID,
    role_name: RoleName,
    tenant_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BILLING_ADMIN")),
):
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    role = await crud_role.get_role_by_name(db, role_name)
    if not role:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Role not found")

    await assign_role_to_user(db, user, role, tenant_id)
    log_audit_event(
        actor_id=str(current_user.id),
        target_id=str(user.id),
        action="assign_role",
        role=role.name,
        tenant_id=str(tenant_id),
    )
    await db.commit()
    await db.refresh(user)
    return RoleReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="Role assigned successfully",
        details=RoleRead.from_orm(role),
    )


# ----------------------
# Deactivate User (no role change)
# ----------------------
@router.post("/{user_id}/deactivate", response_model=UserReadResponse)
async def deactivate_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BILLING_ADMIN")),
):
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="Cannot deactivate yourself"
        )

    # ✅ Only update is_active
    user.is_active = False
    db.add(user)
    await db.commit()
    await db.refresh(user)

    log_audit_event(
        actor_id=str(current_user.id),
        target_id=str(user.id),
        action="deactivate_user",
        tenant_id=None,
    )

    return UserReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="User deactivated successfully",
        details=crud_user.user_to_schema(user),
    )


# ----------------------
# Reactivate User (no role change)
# ----------------------
@router.post("/{user_id}/reactivate", response_model=UserReadResponse)
async def reactivate_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BILLING_ADMIN")),
):
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    # ✅ Only update is_active
    user.is_active = True
    db.add(user)
    await db.commit()
    await db.refresh(user)

    log_audit_event(
        actor_id=str(current_user.id),
        target_id=str(user.id),
        action="reactivate_user",
        tenant_id=None,
    )

    return UserReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="User reactivated successfully",
        details=crud_user.user_to_schema(user),
    )


# ----------------------
# Update User (BILLING_ADMIN or self)
# ----------------------
@router.put("/{user_id}", response_model=UserReadResponse)
async def update_user_endpoint(
    user_id: UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    is_self = user_id == current_user.id
    roles_result = await db.execute(
        text(
            "SELECT r.name FROM user_roles ur JOIN roles r ON r.id = ur.role_id WHERE ur.user_id = :uid"
        ),
        {"uid": str(current_user.id)},
    )
    roles = [row[0] for row in roles_result.fetchall()]
    is_admin = any(r in ["BILLING_ADMIN", "TENANT_ADMIN"] for r in roles)
    if not (is_self or is_admin):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Not authorized")

    updated_user = await crud_user.update_user(db, user, user_in)
    tenant_id = await _get_tenant_id(db, user.id)
    log_audit_event(
        actor_id=str(current_user.id),
        target_id=str(user.id),
        action="update_user",
        tenant_id=tenant_id,
    )

    return UserReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="User updated successfully",
        details=crud_user.user_to_schema(updated_user),
    )


# ----------------------
# Delete User
# ----------------------
@router.delete("/{user_id}", response_model=UserReadResponse)
async def delete_user_endpoint(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("BILLING_ADMIN")),
):
    if user_id == current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Cannot delete yourself")

    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    tenant_id = await _get_tenant_id(db, user.id)
    deleted = await crud_user.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete user"
        )

    log_audit_event(
        actor_id=str(current_user.id),
        target_id=str(user.id),
        action="delete_user",
        tenant_id=tenant_id,
    )

    return UserReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="User deleted successfully",
        details=crud_user.user_to_schema(user),
    )
