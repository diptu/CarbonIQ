from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user, require_roles
from app.models.user import User
from app.schemas.user import UserRead
from app.services.user_service import UserService
from app.core.logger import error_logger

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
    Tenant ID defaults to current_user.tenant_id.
    """
    service = UserService(db=db, tenant_id=current_user.tenant_id)

    try:
        users = await service.get_users(skip=skip, limit=limit)
        out: list[UserRead] = []
        for u in users:
            # Use property call for full_name if it's a @property
            full_name = u.full_name if isinstance(u.full_name, str) else u.full_name()

            data = {
                "id": u.id,
                "email": u.email,
                "full_name": full_name,
                "is_active": u.is_active,
                "tenant_id": u.tenant_id,  # include tenant_id
            }

            out.append(UserRead(**data))
        return out
    except Exception as e:
        error_logger.exception("Error listing users: %s", str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch users")
