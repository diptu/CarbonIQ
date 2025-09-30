"""Role-related API routes with standardized APIResponse."""

from typing import List

from app.api.deps import get_db
from app.crud import role as crud_role
from app.schemas.base import APIResponse
from app.schemas.role import RoleCreate, RoleRead
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/roles", tags=["roles"])

# ----------------------
# Response models for OpenAPI
# ----------------------
RoleReadResponse = create_model(
    "RoleReadResponse", __base__=APIResponse, details=(RoleRead, ...)
)

RoleListResponse = create_model(
    "RoleListResponse", __base__=APIResponse, details=(List[RoleRead], ...)
)


# ----------------------
# 1️⃣ List Roles
# ----------------------
@router.get(
    "/",
    response_model=RoleListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all roles",
    description=(
        "Retrieve a list of all roles in the system.\n\n"
        "- Returns all roles with their `id`, `name`, `description`, and `is_system` flag.\n"
        "- Roles are returned as a list in `details` field of the standardized response."
    ),
)
async def list_roles(db: AsyncSession = Depends(get_db)):
    """List all roles."""
    roles = await crud_role.list_roles(db)
    role_schemas = [RoleRead.from_orm(r) for r in roles]

    return RoleListResponse(
        statusCode=status.HTTP_200_OK,
        msg="Roles retrieved successfully",
        details=role_schemas,
    )


# ----------------------
# 2️⃣ Create Role
# ----------------------
@router.post(
    "/",
    response_model=RoleReadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
    description=(
        "Create a new role in the system.\n\n"
        "- `name`: Unique name of the role.\n"
        "- `description`: Optional description of the role.\n"
        "- `is_system`: Optional flag for system roles (default `False`).\n"
        "- Returns 400 if a role with the same name already exists.\n"
        "- Returns the created role in the standardized `details` field."
    ),
)
async def create_role_endpoint(role_in: RoleCreate, db: AsyncSession = Depends(get_db)):
    """Create a new role."""
    existing_role = await crud_role.get_role_by_name(db, role_in.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_in.name}' already exists",
        )

    role = await crud_role.create_role(db, role_in)
    return RoleReadResponse(
        statusCode=status.HTTP_201_CREATED,
        msg="Role created successfully",
        details=RoleRead.from_orm(role),
    )
