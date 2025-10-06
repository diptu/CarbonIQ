from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.dependencies.rbac import require_roles_or_permissions
from app.models.user import User
from app.schemas.user import UserRead, UserList, UserListResponse
from app.services.user_service import list_users

router = APIRouter()


@router.get("/", response_model=UserListResponse, status_code=status.HTTP_200_OK)
async def get_users(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        require_roles_or_permissions(required_permissions=["view_users"])
    ),
):
    """
    Fetch paginated users for the current tenant.
    """
    try:
        total, users = await list_users(
            db, tenant_id=current_user.tenant_id, skip=skip, limit=limit
        )
        user_schemas: List[UserRead] = [UserRead.from_orm(u) for u in users]

        # Calculate pagination URLs
        last_skip = ((total - 1) // limit) * limit if total > 0 else 0

        def build_url(skip_value: int) -> str | None:
            if 0 <= skip_value < total:
                return str(
                    request.url.replace_query_params(skip=skip_value, limit=limit)
                )
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

    except Exception as e:
        # Log the error for debugging
        import logging

        logging.exception("Failed to fetch user list")
        return {
            "statusCode": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "msg": "Failed to fetch user list",
            "details": str(e),
        }
