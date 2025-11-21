"""Membership API routes for managing tenant memberships."""

import logging
import time
from functools import wraps
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from shared_service.app.core.deps import require_permissions
from shared_service.app.utils.response import APIResponse, build_api_response
from tenant_service.app.core.config import settings
from tenant_service.app.crud.membership import tenant_membership_crud
from tenant_service.app.db.session import get_db
from tenant_service.app.models.membership import TenantMembership
from tenant_service.app.models.tenant import Tenant
from tenant_service.app.schemas.membership import (
    TenantMembershipCreate,
    TenantMembershipUpdate,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/memberships", tags=["memberships"])


USER_SERVICE_URL = settings.USER_SERVICE_URL


# ============================================================
# Helpers
# ============================================================


async def verify_user_exists(user_id: UUID):
    """Call User API to validate user existence."""
    url = f"{USER_SERVICE_URL}/{user_id}"

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(url)
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="User service unavailable. Please try again later.",
        )

    if response.status_code == 404:
        raise HTTPException(
            status_code=400, detail=f"User with ID {user_id} does not exist"
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error from User Service: {response.text}",
        )

    return response.json()  # user data if needed


def verify_tenant_exists(db: Session, tenant_id: UUID):
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=400, detail=f"Tenant with ID {tenant_id} does not exist"
        )
    return tenant


def request_timer(func):
    """Measure request duration in ms."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        response: APIResponse = await func(*args, **kwargs)
        response.meta.request_duration_ms = (time.perf_counter() - start_time) * 1000
        return response

    return wrapper


def fetch_membership_or_404(membership_id: str, db: Session) -> TenantMembership:
    """Find membership or raise 404."""
    try:
        membership_uuid = UUID(membership_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid membership ID format")

    membership = tenant_membership_crud.get(db, membership_uuid)
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return membership


# ============================================================
# Routes
# ============================================================


# ----------------------
# Create Membership
# ----------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permissions(permissions=["membership.create"]))],
)
@request_timer
async def create_membership(
    request: Request,
    obj_in: TenantMembershipCreate,
    db: Session = Depends(get_db),
):
    # ------------------------------------------------------
    # 1️⃣ Validate: Tenant must exist
    # ------------------------------------------------------
    verify_tenant_exists(db, obj_in.tenant_id)

    # ------------------------------------------------------
    # 2️⃣ Validate: User must exist (via User Service API)
    # ------------------------------------------------------
    await verify_user_exists(obj_in.user_id)

    # ------------------------------------------------------
    # 3️⃣ Prevent duplicate membership
    # ------------------------------------------------------
    existing = tenant_membership_crud.get_by_user_and_tenant(
        db, obj_in.user_id, obj_in.tenant_id
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this tenant",
        )

    # ------------------------------------------------------
    # 4️⃣ Create membership
    # ------------------------------------------------------
    membership = tenant_membership_crud.create(db, obj_in)

    return build_api_response(
        request=request,
        result={
            "id": str(membership.id),
            "tenant_id": str(membership.tenant_id),
            "user_id": str(membership.user_id),
            "tenant_role": membership.tenant_role.value,
            "is_active": membership.is_active.value,
        },
        status_code=status.HTTP_201_CREATED,
    )


# ----------------------
# List Memberships
# ----------------------
@router.get(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
@request_timer
async def list_memberships(
    request: Request,
    tenant_id: UUID = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    total = tenant_membership_crud.count_by_tenant(db, tenant_id)
    memberships = tenant_membership_crud.get_by_tenant(db, tenant_id)[
        skip : skip + limit
    ]

    data = [
        {
            "id": str(m.id),
            "tenant_id": str(m.tenant_id),
            "user_id": str(m.user_id),
            "tenant_role": m.tenant_role.value,
            "is_active": m.is_active.value,
        }
        for m in memberships
    ]

    pagination = {
        "count": total,
        "perPage": limit,
        "previousPage": skip - limit if skip - limit >= 0 else None,
        "nextPage": skip + limit if skip + limit < total else None,
    }

    return build_api_response(
        request=request,
        include_user_context=False,
        result={"memberships": data, **pagination},
        status_code=status.HTTP_200_OK,
    )


# ----------------------
# Get Membership by ID
# ----------------------
@router.get(
    "/{membership_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
@request_timer
async def get_membership(
    membership_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    membership = fetch_membership_or_404(membership_id, db)

    return build_api_response(
        request=request,
        result={
            "id": str(membership.id),
            "tenant_id": str(membership.tenant_id),
            "user_id": str(membership.user_id),
            "tenant_role": membership.tenant_role.value,
            "is_active": membership.is_active.value,
        },
        status_code=status.HTTP_200_OK,
    )


# ----------------------
# Get Memberships by User ID
# ----------------------
@router.get(
    "/user/{user_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
@request_timer
async def get_memberships_by_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """Return all memberships for a given user ID."""
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    memberships = tenant_membership_crud.get_by_user_id(db, user_uuid)

    if not memberships:
        raise HTTPException(
            status_code=404,
            detail=f"No memberships found for user_id {user_id}",
        )

    results = [
        {
            "id": str(m.id),
            "tenant_id": str(m.tenant_id),
            "user_id": str(m.user_id),
            "tenant_role": m.tenant_role.value,
            "is_active": m.is_active.value,
        }
        for m in memberships
    ]

    return build_api_response(
        request=request,
        result={"memberships": results, "count": len(results)},
        status_code=status.HTTP_200_OK,
    )


# ----------------------
# Update Membership
# ----------------------
@router.put(
    "/{membership_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
@request_timer
async def update_membership(
    membership_id: str,
    obj_in: TenantMembershipUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    membership = fetch_membership_or_404(membership_id, db)
    updated = tenant_membership_crud.update(db, membership, obj_in)

    return build_api_response(
        request=request,
        result={
            "id": str(updated.id),
            "tenant_role": updated.tenant_role.value,
            "is_active": updated.is_active.value,
            "message": "Membership updated successfully",
        },
        status_code=status.HTTP_200_OK,
    )


# ----------------------
# Delete Membership
# ----------------------
@router.delete(
    "/{membership_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
@request_timer
async def delete_membership(
    membership_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    membership = fetch_membership_or_404(membership_id, db)
    tenant_membership_crud.delete(db, membership.id)

    return build_api_response(
        request=request,
        result={"message": "Membership deleted successfully"},
        status_code=status.HTTP_200_OK,
    )


# ----------------------
# Promote to Admin
# ----------------------
@router.post(
    "/{membership_id}/promote",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
@request_timer
async def promote_to_admin(
    membership_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    membership = tenant_membership_crud.promote_to_admin(db, UUID(membership_id))
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    return build_api_response(
        request=request,
        result={"message": "Member promoted to ADMIN"},
        status_code=status.HTTP_200_OK,
    )


# ----------------------
# Activate / Deactivate Member
# ----------------------
@router.post("/{membership_id}/activate")
@request_timer
async def activate_membership(
    membership_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    membership = tenant_membership_crud.activate(db, UUID(membership_id))
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return build_api_response(
        request=request,
        result={"message": "Membership Activated"},
        status_code=status.HTTP_200_OK,
    )


@router.post("/{membership_id}/deactivate")
@request_timer
async def deactivate_membership(
    membership_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    membership = tenant_membership_crud.deactivate(db, UUID(membership_id))
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    return build_api_response(
        request=request,
        result={"message": "Membership deactivated"},
        status_code=status.HTTP_200_OK,
    )
