from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.db.session import get_db
from app.models.user import User
from app.models.user_roles import UserRole
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.permission import Permission
from app.schemas.user import UserListResponse, UserList, UserRead
from app.schemas.role import RoleRead
from app.schemas.permission import PermissionRead
from app.dependencies.auth import get_current_user
from app.services.user_service import list_users

router = APIRouter()


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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve a paginated list of users with their roles and permissions.
    Requires a valid JWT access token. Uses tenant_id from current user.
    """
    tenant_id: Optional[str] = getattr(current_user, "tenant_id", None)

    # 1️⃣ Fetch users for the tenant
    total, users = await list_users(db, skip=skip, limit=limit, tenant_id=tenant_id)

    if not users:
        details = UserList(
            total=0,
            skip=skip,
            limit=limit,
            previousPage=None,
            nextPage=None,
            firstPage=None,
            lastPage=None,
            items=[],
        )
        return UserListResponse(
            statusCode=200,
            msg="No users found",
            details=details,
        )

    user_ids = [u.id for u in users]

    # 2️⃣ Fetch all roles for these users
    roles_result = await db.execute(
        select(UserRole.user_id, Role)
        .join(Role, Role.id == UserRole.role_id)
        .where(UserRole.user_id.in_(user_ids))
    )
    user_roles_map = {}

    for user_id, role in roles_result.all():
        # Fetch permissions for each role
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

    # 3️⃣ Convert users to UserRead with roles
    items: List[UserRead] = []
    for u in users:
        user_dict = UserRead.from_orm(u).model_dump()
        user_dict["roles"] = user_roles_map.get(u.id, [])
        items.append(UserRead(**user_dict))

    # 4️⃣ Pagination URLs
    def build_page_url(skip_value: int) -> Optional[str]:
        if 0 <= skip_value < total:
            return f"?skip={skip_value}&limit={limit}"
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
        statusCode=200,
        msg="Users retrieved successfully",
        details=details,
    )
