# app/api/v1/routes/users.py
"""User-related API routes with standardized APIResponse, RBAC enforcement, and audit logging."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, Security
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from ima_service.app.api.deps import get_db, require_roles
from ima_service.app.crud import role as crud_role
from ima_service.app.crud import user_basic as crud_user
from ima_service.app.crud.user_roles import assign_role_to_user
from ima_service.app.schemas.base import APIResponse
from ima_service.app.schemas.role import RoleName, RoleRead
from ima_service.app.schemas.user import UserCreate, UserList, UserRead, UserUpdate
from ima_service.app.api.v1.docs.user_docs import (
    ASSIGN_ROLE,
    CREATE_USER,
    DEACTIVATE_USER,
    DELETE_USER,
    GET_USER_BY_ID,
    LIST_USERS,
    REACTIVATE_USER,
    UPDATE_USER,
)
from ima_service.app.utils.audit import log_audit_event

router = APIRouter(prefix="/users", tags=["users"])

# ----------------------
# Response models
# ----------------------
UserReadResponse = create_model(
    "UserReadResponse", __base__=APIResponse, details=(UserRead, ...)
)
UserListResponse = create_model(
    "UserListResponse", __base__=APIResponse, details=(UserList, ...)
)
RoleReadResponse = create_model(
    "RoleReadResponse", __base__=APIResponse, details=(RoleRead, ...)
)


# ----------------------
# Create User
# ----------------------
@router.post(
    "/",
    response_model=UserReadResponse,
    status_code=status.HTTP_201_CREATED,
    summary=CREATE_USER["summary"],
    description=CREATE_USER["description"],
)
async def create_user_endpoint(
    user_in: UserCreate,
    claims: dict = Security(require_roles("TENANT_ADMIN", "BILLING_ADMIN", "MEMBER")),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user within the same tenant as the actor.
    The new user is always assigned the default VIEWER role.
    """
    tenant_id = claims.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot determine tenant from your credentials",
        )

    # Check if email already exists within this tenant
    existing_user = await crud_user.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user_in.email}' already exists.",
        )

    # Create user with tenant association
    db_user = await crud_user.create_user(db, user_in, tenant_id=tenant_id)

    # Assign default VIEWER role
    viewer_role = await crud_role.get_role_by_name(db, RoleName.VIEWER)
    if viewer_role:
        await assign_role_to_user(db, db_user, viewer_role, tenant_id=tenant_id)

    # Audit log
    log_audit_event(
        actor_id=str(claims.get("sub")),
        target_id=str(db_user.id),
        action="create_user",
        role=RoleName.VIEWER.value if viewer_role else None,
        tenant_id=tenant_id,
    )

    await db.refresh(db_user)
    return UserReadResponse(
        statusCode=status.HTTP_201_CREATED,
        msg="User created successfully",
        details=crud_user.user_to_schema(db_user),
    )


# ----------------------
# Assign Role
# ----------------------
@router.post(
    "/{user_id}/roles",
    response_model=RoleReadResponse,
    status_code=status.HTTP_200_OK,
    summary=ASSIGN_ROLE["summary"],
    description=ASSIGN_ROLE["description"],
)
async def assign_role_to_user_endpoint(
    user_id: UUID,
    role_name: RoleName = Query(..., description="Select a role"),
    tenant_id: UUID | None = Query(None, description="Optional tenant ID"),
    claims: dict = Security(require_roles("TENANT_ADMIN")),
    db: AsyncSession = Depends(get_db),
):
    """Assign or update a role for a user, optionally scoped to a tenant."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{user_id}' not found."
        )

    role = await crud_role.get_role_by_name(db, role_name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_name.value}' not found.",
        )

    existing_role = next(
        (r for r in user.roles if getattr(r, "tenant_id", None) == tenant_id), None
    )
    if existing_role:
        await crud_user.update_user_role(db, user, existing_role, role, tenant_id)
    else:
        await assign_role_to_user(db, user, role, tenant_id=tenant_id)

    log_audit_event(
        actor_id=str(claims.get("sub")),
        target_id=str(user.id),
        action="assign_role",
        role=role.name,
        tenant_id=str(tenant_id) if tenant_id else None,
    )

    await db.commit()
    await db.refresh(user)

    return RoleReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="Role assigned successfully",
        details=RoleRead.from_orm(role),
    )


# ----------------------
# List Users
# ----------------------
@router.get(
    "/",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary=LIST_USERS["summary"],
    description=LIST_USERS["description"],
)
async def list_users_endpoint(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    claims: dict = Security(
        require_roles("VIEWER")
    ),  # keep VIEWER; hierarchy will expand
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a paginated list of users."""
    total, users = await crud_user.list_users(db, skip=skip, limit=limit)
    user_schemas = [crud_user.user_to_schema(u) for u in users]

    last_skip = ((total - 1) // limit) * limit if total > 0 else 0

    def build_url(skip_value: int) -> str | None:
        if 0 <= skip_value < total:
            return str(request.url.replace_query_params(skip=skip_value, limit=limit))
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


# ----------------------
# Get User by ID
# ----------------------
@router.get(
    "/{user_id}",
    response_model=UserReadResponse,
    status_code=status.HTTP_200_OK,
    summary=GET_USER_BY_ID["summary"],
    description=GET_USER_BY_ID["description"],
)
async def get_user_endpoint(
    user_id: UUID,
    claims: dict = Security(require_roles("TENANT_ADMIN", "MANAGER", "VIEWER")),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a single user by their unique ID (UUID)."""
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found.",
        )

    return UserReadResponse(
        statusCode=status.HTTP_200_OK,
        msg="User retrieved successfully",
        details=crud_user.user_to_schema(user),
    )
