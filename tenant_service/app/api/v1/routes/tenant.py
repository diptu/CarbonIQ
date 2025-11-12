"""Tenant API routes for managing multi-tenant entities."""

import time
from functools import wraps
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from shared_service.app.core.deps import get_current_user
from shared_service.app.utils.response import APIResponse, build_api_response
from tenant_service.app.crud.tenant import tenant_crud
from tenant_service.app.db.session import get_db
from tenant_service.app.models.tenant import Tenant
from tenant_service.app.schemas.tenant import TenantCreate

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


# # ----------------------
# # List Tenants
# # ----------------------
# @router.get(
#     "/",
#     response_model=APIResponse,
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(require_permissions(["tenant.read"]))],
#     openapi_extra={"security": [{"BearerAuth": []}]},
# )
# @request_timer
# async def list_tenants(
#     request: Request,
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_cached_current_user),
# ):
#     total = tenant_crud.count(db)
#     tenants = tenant_crud.get_all(db, skip=skip, limit=limit)

#     data = [
#         {
#             "id": str(t.id),
#             "name": t.name,
#             "schema_name": t.schema_name,
#             "is_active": t.is_active,
#         }
#         for t in tenants
#     ]

#     pagination = {
#         "count": total,
#         "perPage": limit,
#         "previousPage": skip - limit if skip - limit >= 0 else None,
#         "nextPage": skip + limit if skip + limit < total else None,
#     }

#     return build_api_response(
#         request=request,
#         current_user=current_user,
#         result={"tenants": data, **pagination},
#         status_code=status.HTTP_200_OK,
#     )


# # ----------------------
# # Get Tenant by ID
# # ----------------------
# @router.get(
#     "/{tenant_id}",
#     response_model=APIResponse,
#     dependencies=[Depends(require_permissions(["tenant.read"]))],
# )
# @request_timer
# async def get_tenant(
#     tenant_id: str,
#     request: Request,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_cached_current_user),
# ):
#     tenant = fetch_tenant_or_404(tenant_id, db)
#     domains = tenant_domain_crud.get_by_tenant(db, tenant.id)
#     return build_api_response(
#         request=request,
#         current_user=current_user,
#         result={
#             "id": str(tenant.id),
#             "name": tenant.name,
#             "schema_name": tenant.schema_name,
#             "is_active": tenant.is_active,
#             "domains": [d.domain for d in domains],
#         },
#         status_code=status.HTTP_200_OK,
#     )


# # ----------------------
# # Update Tenant
# # ----------------------
# @router.put(
#     "/{tenant_id}",
#     response_model=APIResponse,
#     dependencies=[Depends(require_permissions(["tenant.update"]))],
# )
# @request_timer
# async def update_tenant(
#     tenant_id: str,
#     tenant_in: TenantUpdate,
#     request: Request,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_cached_current_user),
# ):
#     tenant = fetch_tenant_or_404(tenant_id, db)
#     tenant = tenant_crud.update(db, tenant, tenant_in)
#     return build_api_response(
#         request=request,
#         current_user=current_user,
#         result={"id": str(tenant.id), "name": tenant.name},
#         status_code=status.HTTP_200_OK,
#     )


# # ----------------------
# # Delete Tenant
# # ----------------------
# @router.delete(
#     "/{tenant_id}",
#     response_model=APIResponse,
#     dependencies=[Depends(require_permissions(["tenant.delete"]))],
# )
# @request_timer
# async def delete_tenant(
#     tenant_id: str,
#     request: Request,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_cached_current_user),
# ):
#     tenant = fetch_tenant_or_404(tenant_id, db)
#     tenant_crud.delete(db, tenant.id)
#     return build_api_response(
#         request=request,
#         current_user=current_user,
#         result={"message": f"Tenant '{tenant.name}' deleted successfully"},
#         status_code=status.HTTP_200_OK,
#     )


# # ----------------------
# # Activate Tenant
# # ----------------------
# @router.post(
#     "/{tenant_id}/activate",
#     response_model=APIResponse,
#     dependencies=[Depends(require_permissions(["tenant.update"]))],
# )
# @request_timer
# async def activate_tenant(
#     tenant_id: str,
#     request: Request,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_cached_current_user),
# ):
#     tenant = fetch_tenant_or_404(tenant_id, db)
#     tenant_crud.activate(db, tenant.id)
#     return build_api_response(
#         request=request,
#         current_user=current_user,
#         result={"message": f"Tenant '{tenant.name}' activated successfully"},
#         status_code=status.HTTP_200_OK,
#     )


# # ----------------------
# # Deactivate Tenant
# # ----------------------
# @router.post(
#     "/{tenant_id}/deactivate",
#     response_model=APIResponse,
#     dependencies=[Depends(require_permissions(["tenant.update"]))],
# )
# @request_timer
# async def deactivate_tenant(
#     tenant_id: str,
#     request: Request,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_cached_current_user),
# ):
#     tenant = fetch_tenant_or_404(tenant_id, db)
#     tenant_crud.deactivate(db, tenant.id)
#     return build_api_response(
#         request=request,
#         current_user=current_user,
#         result={"message": f"Tenant '{tenant.name}' deactivated successfully"},
#         status_code=status.HTTP_200_OK,
#     )
