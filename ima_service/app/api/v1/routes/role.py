"""Role-related API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.role import RoleRead, RoleCreate, RoleName
from app.crud import role as crud_role
from app.api.deps import get_db

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=List[RoleRead])
async def get_roles_endpoint(db: AsyncSession = Depends(get_db)):
    """Retrieve all roles."""
    return await crud_role.get_roles(db)


@router.post("/", response_model=RoleRead)
async def create_role_endpoint(role_in: RoleCreate, db: AsyncSession = Depends(get_db)):
    """Create a new role."""
    existing_role = await crud_role.get_role_by_name(db, role_in.name)
    if existing_role:
        raise HTTPException(
            status_code=400, detail=f"Role '{role_in.name}' already exists"
        )
    return await crud_role.create_role(db, role_in)
