# app/api/v1/routes/user_router.py
"""User CRUD API routes for IMA Service with fixed multi-tenant RBAC."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.db.session import get_db
from app.models.user import User
from app.models.user_roles import UserRole
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.schemas.user import UserCreate, UserRead, UserList, UserListResponse
from app.schemas.role import RoleRead
from app.schemas.permission import PermissionRead
from app.dependencies.auth import get_current_user
from app.services.user_service import create_user, list_users
from ima_service.app.dependencies.rbac import require_roles

router = APIRouter()


# ---------------------------------------------------------------------------
# 📋 Create New User (Fixed)
# ---------------------------------------------------------------------------
@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(["BILLING_ADMIN"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def create_new_user(
    user_in: UserCreate,
    tenant_id: Optional[UUID] = Query(
        None, description="Tenant ID. Defaults to current user's tenant."
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = tenant_id or current_user.tenant_id

    # -------------------------------
    # ✅ Tenant validation (same or child only)
    # -------------------------------
    query = text("""
        SELECT id FROM tenants
        WHERE id = :tenant_id
          AND (id = :current_tenant_id OR parent_id = :current_tenant_id)
    """)
    result = await db.execute(
        query,
        {"tenant_id": str(tenant_id), "current_tenant_id": str(current_user.tenant_id)},
    )
    valid_tenant = result.scalar()
    if not valid_tenant:
        raise HTTPException(
            status_code=403, detail="Cannot create user under unrelated tenant"
        )

    # -------------------------------
    # ✅ Create user
    # -------------------------------
    try:
        new_user = await create_user(
            db=db,
            email=user_in.email,
            password=user_in.password,
            creator_tenant_id=current_user.tenant_id,
            tenant_id=tenant_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

    # -------------------------------
    # ✅ Assign default VIEWER role if not already assigned
    # -------------------------------
    default_role_result = await db.execute(select(Role).where(Role.name == "VIEWER"))
    default_role = default_role_result.scalar_one_or_none()

    if default_role:
        role_exists_result = await db.execute(
            select(UserRole)
            .where(UserRole.user_id == new_user.id)
            .where(UserRole.role_id == default_role.id)
            .where(UserRole.tenant_id == tenant_id)
        )
        existing_role = role_exists_result.scalar_one_or_none()

        if not existing_role:
            db.add(
                UserRole(
                    user_id=new_user.id, role_id=default_role.id, tenant_id=tenant_id
                )
            )
            await db.commit()
            await db.refresh(new_user)

    return UserRead.from_orm(new_user)


# ---------------------------------------------------------------------------
# 📋 List Users (Fixed)
# ---------------------------------------------------------------------------
@router.get(
    "/",
    response_model=UserListResponse,
    dependencies=[Depends(get_current_user)],
    status_code=status.HTTP_200_OK,
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    include_inactive: bool = Query(False, description="Include inactive users"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve paginated users for current tenant and child tenants.
    """
    tenant_id = current_user.tenant_id

    # ✅ Fetch users using service with proper tenant filtering
    total, users = await list_users(
        db,
        skip=skip,
        limit=limit,
        tenant_id=tenant_id,
        include_inactive=include_inactive,
    )

    if not users:
        return UserListResponse(
            statusCode=200,
            msg="No users found",
            details=UserList(
                total=0,
                skip=skip,
                limit=limit,
                previousPage=None,
                nextPage=None,
                firstPage=None,
                lastPage=None,
                items=[],
            ),
        )

    user_ids = [u.id for u in users]

    # ✅ Fetch roles and permissions
    user_roles_map = {}
    roles_result = await db.execute(
        select(UserRole.user_id, Role)
        .join(Role, Role.id == UserRole.role_id)
        .where(UserRole.user_id.in_(user_ids))
    )

    for user_id, role in roles_result.all():
        perm_result = await db.execute(
            select(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .where(RolePermission.role_id == role.id)
        )
        permissions = [PermissionRead.from_orm(p) for p in perm_result.scalars().all()]
        role_read = RoleRead.from_orm(role).model_copy(
            update={"permissions": permissions}
        )
        user_roles_map.setdefault(user_id, []).append(role_read)

    # ✅ Assemble users
    items = []
    for u in users:
        user_dict = UserRead.from_orm(u).model_dump()
        user_dict["roles"] = user_roles_map.get(u.id, [])
        items.append(UserRead(**user_dict))

    # ✅ Pagination
    def build_page_url(skip_value: int) -> Optional[str]:
        if 0 <= skip_value < total:
            return (
                f"?skip={skip_value}&limit={limit}&include_inactive={include_inactive}"
            )
        return None

    last_skip = ((total - 1) // limit) * limit if total > 0 else 0
    details = UserList(
        total=total,
        skip=skip,
        limit=limit,
        previousPage=build_page_url(skip - limit),
        nextPage=build_page_url(skip + limit),
        firstPage=build_page_url(0),
        lastPage=build_page_url(last_skip),
        items=items,
    )

    return UserListResponse(
        statusCode=200, msg="Users retrieved successfully", details=details
    )
