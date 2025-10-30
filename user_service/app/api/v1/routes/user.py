from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles_permissions
from app.crud.user import user_crud
from app.db.session import get_db
from app.schemas.user import UserCreate

# from app.shared.utils.response import build_response

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles_permissions(roles=["admin"], permissions=["user.create"]))],
)
def create_user(
    user_in: UserCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    db_user = user_crud.get_by_email(db, user_in.email)
    if db_user:
        # return build_response(error="Email already registered", user_id=current_user.id)
        return {"data": db_user}
    user = user_crud.create(db, user_in)
    return user
    # return build_response(
    #     data={"id": str(user.id), "email": user.email},
    #     user_id=current_user.id,
    #     tenant_id=getattr(current_user, "tenant_id", None),
    #     roles=[r.role.name for r in current_user.roles],
    #     permissions=[p.permission.name for p in current_user.user_permissions],
    # )


@router.get(
    "/",
    dependencies=[Depends(require_roles_permissions(roles=["VIEWER"], permissions=["user.read"]))],
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    users = user_crud.get_all(db, skip=skip, limit=limit)
    users_data = [{"id": str(u.id), "email": u.email} for u in users]
    return build_response(
        data=users_data,
        user_id=current_user.id,
        tenant_id=getattr(current_user, "tenant_id", None),
        roles=[r.role.name for r in current_user.roles],
        permissions=[p.permission.name for p in current_user.user_permissions],
    )
