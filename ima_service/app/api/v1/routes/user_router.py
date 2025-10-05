from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.rbac import require_roles_or_permissions
from app.models.user import User
from app.schemas.user import UserCreate, UserListResponse, UserReadResponse
from app.services.user_service import create_user, list_users

router = APIRouter()


@router.post("/", response_model=UserReadResponse)
async def create_new_user(
    user_in: UserCreate,
    current_user: User = Depends(
        require_roles_or_permissions(required_permissions=["manage_users"])
    ),
    db: Session = Depends(get_db),
):
    user = create_user(db, user_in)
    return {"statusCode": 201, "msg": "User created", "details": user}


@router.get("/", response_model=UserListResponse)
async def get_users(
    current_user: User = Depends(
        require_roles_or_permissions(required_permissions=["view_users"])
    ),
    db: Session = Depends(get_db),
):
    users = list_users(db)
    return {"statusCode": 200, "msg": "User list fetched", "details": users}
