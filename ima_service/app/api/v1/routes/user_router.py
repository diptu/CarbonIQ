# app/api/v1/routes/user_router.py
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User
from app.schemas.user import UserRead
from app.services.user_service import UserService
from app.core.logger import audit_logger, error_logger

router = APIRouter()


@router.get(
    "/",
    response_model=List[UserRead],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(["MEMBER"])),
):
    """
    Get all users in the current tenant (paginated).
    Tenant ID defaults to current_user's tenant.
    """
    service = UserService(db=db, tenant_id=current_user.tenant_id)

    try:
        users = await service.get_users(skip=skip, limit=limit)
        return [UserRead(**user.to_dict()) for user in users]
    except Exception as e:
        error_logger.exception(f"Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")
