# app/api/v1/routes/role.py
"""Role-related API routes with standardized APIResponse."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import create_model

from app.schemas.role import RoleRead, RoleCreate
from app.crud import role as crud_role
from app.api.deps import get_db
from app.schemas.base import APIResponse

router = APIRouter(prefix="/roles", tags=["roles"])

# ----------------------
# Concrete response models for OpenAPI
# ----------------------
RoleReadResponse = create_model(
    "RoleReadResponse", __base__=APIResponse, details=(RoleRead, ...)
)

RoleListResponse = create_model(
    "RoleListResponse", __base__=APIResponse, details=(List[RoleRead], ...)
)


# ----------------------
# List Roles
# ----------------------
@router.get("/", response_model=RoleListResponse)
async def list_roles(db: AsyncSession = Depends(get_db)):
    """List all roles."""
    roles = await crud_role.list_roles(db)
    role_schemas = [RoleRead.from_orm(r) for r in roles]

    return RoleListResponse(
        statusCode=200,
        msg="Roles retrieved successfully",
        details=role_schemas,
    )


# ----------------------
# Create Role
# ----------------------
@router.post("/", response_model=RoleReadResponse, status_code=status.HTTP_201_CREATED)
async def create_role_endpoint(role_in: RoleCreate, db: AsyncSession = Depends(get_db)):
    """Create a new role with standardized response."""
    existing_role = await crud_role.get_role_by_name(db, role_in.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role_in.name}' already exists",
        )

    role = await crud_role.create_role(db, role_in)
    return RoleReadResponse(
        statusCode=201,
        msg="Role created successfully",
        details=RoleRead.from_orm(role),
    )
