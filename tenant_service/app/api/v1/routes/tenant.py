"""Tenant API routes for managing multi-tenant entities."""

import logging
import time
from functools import wraps
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared_service.app.core.deps import get_current_user, require_permissions
from shared_service.app.utils.response import APIResponse, build_api_response
from tenant_service.app.crud.tenant import tenant_crud
from tenant_service.app.db.session import get_db
from tenant_service.app.models.tenant import Tenant
from tenant_service.app.schemas.tenant import TenantCreate, TenantUpdate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set debug mode


class TenantUpdateForbidden(Exception):
    """Raised when a child tenant attempts forbidden updates"""

    def __init__(self, message: str):
        self.message = message


router = APIRouter(prefix="/tenants", tags=["tenants"])


# ============================================================
# Helpers
# ============================================================


def request_timer(func):
    """Measure request duration in ms."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        response: APIResponse = await func(*args, **kwargs)
        response.meta.request_duration_ms = (time.perf_counter() - start_time) * 1000
        return response

    return wrapper


def get_cached_current_user(request: Request, db: Session = Depends(get_db)):
    """Cache current user for request scope."""
    if hasattr(request.state, "current_user"):
        return request.state.current_user
    user = get_current_user(db=db)
    request.state.current_user = user
    return user


def fetch_tenant_or_404(tenant_id: str, db: Session) -> Tenant:
    """Find tenant or raise HTTP 404."""
    try:
        tenant_uuid = UUID(tenant_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tenant ID format")
    tenant = tenant_crud.get(db, tenant_uuid)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant


# ============================================================
# Routes
# ============================================================


# ----------------------
# create Tenants
# ----------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_permissions(permissions=["tenant.create"]))],
    # openapi_extra={"security": [{"BearerAuth": []}]},
)
async def create_tenant(
    request: Request,
    tenant_in: TenantCreate,
    db: Session = Depends(get_db),
    # current_user: User = Depends(get_cached_current_user),
):
    # Check if tenant already exists
    existing = tenant_crud.get_by_name(db, tenant_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Tenant name already exists")

    try:
        # Create tenant using ORM; tables and schema are auto-created
        tenant = tenant_crud.create(db, tenant_in)

        return build_api_response(
            request=request,
            result={
                "id": str(tenant.id),
                "name": tenant.name,
                "schema": tenant.schema_name,
            },
            status_code=status.HTTP_201_CREATED,
            meta_extra={"source": "tenant_service"},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create tenant: {e}")


# ----------------------
# List Tenants
# ----------------------
@router.get(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(require_permissions(["tenant.read"]))],
    # openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def list_tenants(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    active_only: bool = Query(True, description="Return only active tenants"),
    db: Session = Depends(get_db),
    # current_user=Depends(get_cached_current_user),
):
    total = tenant_crud.count(db, active_only=active_only)
    tenants = tenant_crud.get_all(db, skip=skip, limit=limit, active_only=active_only)

    data = [
        {
            "id": str(t.id),
            "name": t.name,
            "schema_name": t.schema_name,
            "status": t.status,
            "plan": t.plan,
        }
        for t in tenants
    ]

    pagination = {
        "count": total,
        "perPage": limit,
        "previousPage": skip - limit if skip - limit >= 0 else None,
        "nextPage": skip + limit if skip + limit < total else None,
    }

    return build_api_response(
        request=request,
        # current_user=current_user,
        include_user_context=False,
        result={"tenants": data, **pagination},
        status_code=status.HTTP_200_OK,
    )


# # ----------------------
# # Get Tenant by ID
# # ----------------------
@router.get(
    "/{tenant_id}",
    response_model=APIResponse,
    #     dependencies=[Depends(require_permissions(["tenant.read"]))],
    #     openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def get_tenant(
    tenant_id: str,
    request: Request,
    db: Session = Depends(get_db),
    # current_user=Depends(get_cached_current_user),
):
    tenant = fetch_tenant_or_404(tenant_id, db)
    # domains = tenant_domain_crud.get_by_tenant(db, tenant.id)
    return build_api_response(
        request=request,
        # current_user=current_user,
        include_user_context=False,
        result={
            "id": str(tenant.id),
            "name": tenant.name,
            "schema_name": tenant.schema_name,
            "status": tenant.status,
            "plan": tenant.plan,
            # "domains": [d.domain for d in domains],
        },
        status_code=status.HTTP_200_OK,
    )


# ----------------------
# Update Tenant
# ----------------------
@router.put(
    "/{tenant_id}",
    response_model=None,
)
@request_timer
async def update_tenant(
    tenant_id: str,
    tenant_in: TenantUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    logger.info(f"[TenantUpdate] Starting update for tenant_id={tenant_id}")

    try:
        tenant = fetch_tenant_or_404(tenant_id, db)
        logger.debug(
            f"[TenantUpdate] Fetched tenant '{tenant.name}' "
            f"(Type={'Parent' if tenant.parent_id is None else 'Child'})"
        )

        tenant = tenant_crud.update(db, tenant, tenant_in)

        logger.info(f"[TenantUpdate] Tenant '{tenant.name}' updated successfully")

        return build_api_response(
            request=request,
            include_user_context=False,
            result={
                "id": str(tenant.id),
                "name": tenant.name,
                "status": tenant.status,
                "schema": tenant.schema_name,
                "plan": tenant.plan,
                "message": f"Tenant '{tenant.name}' updated successfully",
            },
            status_code=status.HTTP_200_OK,
        )

    except ValueError as ve:
        # Expected: trying to change plan/status on a child tenant
        logger.warning(f"[TenantUpdate] Business rule violation: {ve}")

        return build_api_response(
            request=request,
            include_user_context=False,
            result={
                "error": "InvalidOperation",
                "message": str(ve),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        logger.exception(
            f"[TenantUpdate] Unexpected error updating tenant '{tenant_id}': {e}"
        )

        return build_api_response(
            request=request,
            include_user_context=False,
            result={
                "error": "InternalServerError",
                "message": "An unexpected error occurred during tenant update.",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ----------------------
# Delete Tenant
# ----------------------
@router.delete(
    "/{tenant_id}",
    response_model=APIResponse,
    # dependencies=[Depends(require_permissions(["tenant.delete"]))],
    # openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def delete_tenant(
    tenant_id: str,
    request: Request,
    db: Session = Depends(get_db),
    # current_user=Depends(get_cached_current_user),
    cascade_children: bool = False,  # optional query param
    soft_delete: bool = False,  # optional query param
):
    tenant = fetch_tenant_or_404(tenant_id, db)
    try:
        tenant_crud.delete(
            db,
            tenant.id,
            soft_delete=soft_delete,
            cascade_children=cascade_children,
        )
        return build_api_response(
            request=request,
            # current_user=current_user,
            include_user_context=False,
            result={"message": f"Tenant '{tenant.name}' deleted successfully"},
            status_code=status.HTTP_200_OK,
        )
    except ValueError as ve:
        # Logical errors like child tenants exist
        return build_api_response(
            request=request,
            include_user_context=False,
            result={"error": str(ve)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except RuntimeError as re:
        # Server-side errors like schema drop failure
        return build_api_response(
            request=request,
            include_user_context=False,
            result={"error": str(re)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception:
        # Catch-all for unexpected errors
        return build_api_response(
            request=request,
            include_user_context=False,
            result={"error": "An unexpected error occurred."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# Shared private function


async def _handle_status_change(
    tenant_id: str,
    request: Request,
    db: Session,
    # current_user=Depends(get_cached_current_user),
    action: str,
):
    actions = {
        "activate": tenant_crud.activate,
        "suspend": tenant_crud.suspend,
        "deactivate": tenant_crud.deactivate,
    }

    if action not in actions:
        raise HTTPException(status_code=400, detail="Invalid action")

    tenant = fetch_tenant_or_404(tenant_id, db)

    try:
        # Apply action on the main tenant
        updated_tenant = actions[action](db, tenant.id)
    except ValueError as ve:
        # Catch business rule violations
        logger.warning(f"Status change failed: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Unexpected error during status change: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

    # Cascade to child tenants if parent
    if updated_tenant and updated_tenant.id:
        db.execute(
            text("""
                UPDATE tenants
                SET status = :status
                WHERE parent_id = :parent_id
            """),
            {
                "status": updated_tenant.status.value,
                "parent_id": updated_tenant.id,
            },
        )
        db.commit()
        logger.info(
            f"Cascaded {action} to all child tenants of '{updated_tenant.name}'"
        )

    return build_api_response(
        request=request,
        include_user_context=False,
        result={"message": f"Tenant '{tenant.name}' {action}d successfully"},
        status_code=status.HTTP_200_OK,
    )


# ----------------------
# activate Tenant
# ----------------------


@router.post(
    "/{tenant_id}/activate",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["tenant.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def activate_tenant(
    tenant_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    return await _handle_status_change(tenant_id, request, db, "activate")


# ----------------------
# suspend Tenant
# ----------------------
@router.post(
    "/{tenant_id}/suspend",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["tenant.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def suspend_tenant(
    tenant_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    return await _handle_status_change(tenant_id, request, db, "suspend")


# ----------------------
# deactivate Tenant
# ----------------------
@router.post(
    "/{tenant_id}/deactivate",
    response_model=APIResponse,
    dependencies=[Depends(require_permissions(["tenant.update"]))],
    openapi_extra={"security": [{"BearerAuth": []}]},
)
@request_timer
async def deactivate_tenant(
    tenant_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    return await _handle_status_change(tenant_id, request, db, "deactivate")
