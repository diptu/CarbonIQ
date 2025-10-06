# app/api/v1/routes/user_router.py
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserListResponse, UserList
from app.services.user_service import list_users
from app.dependencies.auth import get_current_user

router = APIRouter()

from app.schemas.user import UserRead


@router.get(
    "/",
    response_model=UserListResponse,
    dependencies=[Depends(get_current_user)],  # Protect endpoint
    status_code=status.HTTP_200_OK,
    openapi_extra={"security": [{"BearerAuth": []}]},  # Show Swagger Bearer token
)
async def get_users(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    """
    Retrieve a paginated list of users.
    Requires a valid JWT access token.
    """
    total, users = await list_users(db, skip=skip, limit=limit)

    # Convert SQLAlchemy users to Pydantic models
    items = [UserRead.from_orm(u) for u in users]

    details = UserList(
        total=total,
        skip=skip,
        limit=limit,
        previousPage=None,  # Add logic if needed
        nextPage=None,  # Add logic if needed
        firstPage=None,
        lastPage=None,
        items=items,
    )

    return UserListResponse(
        statusCode=200,
        msg="Users retrieved successfully",
        details=details,
    )


# @router.get(
#     "/",
#     response_model=UserListResponse,
#     dependencies=[Depends(get_current_user)],  # Protect endpoint with JWT
#     status_code=status.HTTP_200_OK,
#     openapi_extra={"security": [{"BearerAuth": []}]},  # Show Swagger Bearer token
# )
# async def get_users(
#     skip: int = Query(0, ge=0, description="Number of items to skip"),
#     limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
#     db: AsyncSession = Depends(get_db),
# ):
#     """
#     Retrieve a paginated list of users.
#     Requires a valid JWT access token.
#     """
#     total, users = await list_users(db, skip=skip, limit=limit)

#     # Return minimal response
#     return {"total": total, "items": users}
