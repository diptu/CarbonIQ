# app/api/v1/routes/user_router.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.dependencies.auth import require_roles
from app.models.user import User
from app.schemas.user import UserRead
from app.services.user_service import UserService
from app.core.logger import error_logger

router = APIRouter()


@router.get("/", response_model=dict, openapi_extra={"security": [{"BearerAuth": []}]})
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, gt=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["MEMBER"])),
):
    """
    Get all users in the current tenant (paginated).
    Returns nextPage, prevPage, totalCount, and items.
    """
    service = UserService(db=db, tenant_id=current_user.tenant_id)

    try:
        users, total_count = await service.get_users(
            skip=skip, limit=limit, return_count=True
        )

        items: list[UserRead] = []
        for u in users:
            data = {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,  # safe property access
                "is_active": u.is_active,
                "tenant_id": u.tenant_id,
            }
            items.append(UserRead(**data))

        next_page = skip + limit if skip + limit < total_count else None
        prev_page = skip - limit if skip - limit >= 0 else None

        return {
            "items": items,
            "totalCount": total_count,
            "nextPage": next_page,
            "prevPage": prev_page,
        }

    except Exception as e:
        error_logger.exception("Error listing users: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch users")
