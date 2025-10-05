from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.dependencies.auth import require_permissions
from app.models.user import User
from app.schemas.role import RoleCreate, RoleRead
from app.services.role_service import create_role, list_roles, assign_role_to_user
from app.db.session import get_db
from app.dependencies.rbac import require_roles_or_permissions

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=RoleRead)
async def add_role(
    role_in: RoleCreate,
    current_user: User = Depends(
        require_roles_or_permissions(required_permissions=["manage_roles"])
    ),
    db: Session = Depends(get_db),
):
    """
    Create a new role.
    Only users with 'manage_roles' permission can create roles.
    """
    role = create_role(db, role_in)
    return {"statusCode": 201, "msg": "Role created", "details": role}


@router.get("/", response_model=List[RoleRead])
async def get_roles(
    current_user: User = Depends(
        require_roles_or_permissions(required_permissions=["view_roles"])
    ),
    db: Session = Depends(get_db),
):
    """
    List all roles.
    Users need 'view_roles' permission.
    """
    roles = list_roles(db)
    return {"statusCode": 200, "msg": "Roles fetched", "details": roles}


@router.post("/{role_id}/assign/{user_id}")
async def assign_role(
    role_id: str,
    user_id: str,
    current_user: User = Depends(
        require_roles_or_permissions(required_permissions=["manage_roles"])
    ),
    db: Session = Depends(get_db),
):
    """
    Assign a role to a user.
    Requires 'manage_roles' permission.
    """
    assign_role_to_user(db, role_id, user_id, current_user.tenant_id)
    return {"statusCode": 200, "msg": "Role assigned to user", "details": None}
