"""
Role-related API routes with standardized APIResponse.
"""

from typing import List

from app.api.deps import get_db
from app.crud import role as crud_role
from app.schemas.base import APIResponse
from app.schemas.role import RoleCreate, RoleRead
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import create_model
from sqlalchemy.ext.asyncio import AsyncSession

from ima_service.app.api.v1.docs.role_docs import CREATE_ROLE, LIST_ROLES

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
    summary=LIST_ROLES["summary"],
    description=LIST_ROLES["description"],
)
async def list_roles(db: AsyncSession = Depends(get_db)):
    """
    List all roles in the system.

    Parameters
    ----------
    db : AsyncSession, optional
        SQLAlchemy async session.

    Returns
    -------
    RoleListResponse
        Standardized response containing a list of roles.
    """
    roles = await crud_role.list_roles(db)
    role_schemas = [RoleRead.from_orm(r) for r in roles]

    return RoleListResponse(
        statusCode=status.HTTP_200_OK,
        msg="Roles retrieved successfully",
        details=role_schemas,
    )


# # ----------------------
# # 2️⃣ Create Role
# # ----------------------
# @router.post(
#     "/",
#     response_model=RoleReadResponse,
#     status_code=status.HTTP_201_CREATED,
#     summary=CREATE_ROLE["summary"],
#     description=CREATE_ROLE["description"],
# )
# async def create_role_endpoint(role_in: RoleCreate, db: AsyncSession = Depends(get_db)):
#     """
#     Create a new role in the system.

#     Parameters
#     ----------
#     role_in : RoleCreate
#         Input schema containing role name (must be one of RoleName enum),
#         optional description, and optional is_system flag.
#     db : AsyncSession, optional
#         SQLAlchemy async session.

#     Returns
#     -------
#     RoleReadResponse
#         Standardized response with the created role details.

#     Raises
#     ------
#     HTTPException
#         400 Bad Request if a role with the same name already exists.

#     Notes
#     -----
#     The `name` field in RoleCreate must be one of the following enum values:
#     - {RoleName.__members__.keys()}
#     """
#     existing_role = await crud_role.get_role_by_name(db, role_in.name)
#     if existing_role:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Role '{role_in.name}' already exists",
#         )

#     role = await crud_role.create_role(db, role_in)
#     return RoleReadResponse(
#         statusCode=status.HTTP_201_CREATED,
#         msg="Role created successfully",
#         details=RoleRead.from_orm(role),
#     )
