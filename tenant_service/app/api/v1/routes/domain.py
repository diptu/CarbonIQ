"""Domain API routes for managing tenant domains."""

import logging
import time
from functools import wraps
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from shared_service.app.utils.response import APIResponse, build_api_response
from tenant_service.app.crud.domain import domain_crud
from tenant_service.app.db.session import get_db
from tenant_service.app.models.domain import TenantDomain
from tenant_service.app.schemas.domain import DomainCreate, DomainUpdate

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

router = APIRouter(prefix="/domains", tags=["domains"])


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


def fetch_domain_or_404(domain_id: str, db: Session) -> TenantDomain:
    """Find domain or raise HTTP 404."""
    try:
        domain_uuid = UUID(domain_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid domain ID format")
    domain = domain_crud.get(db, domain_uuid)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain


# ============================================================
# Routes
# ============================================================


# ----------------------
# Create Domain
# ----------------------
@router.post(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    # dependencies=[Depends(require_permissions(permissions=["domain.create"]))],
    # dependencies=[Depends(require_permissions(["domain.create"]))],
)
@request_timer
async def create_domain(
    request: Request,
    domain_in: DomainCreate,
    db: Session = Depends(get_db),
):
    existing = domain_crud.get_by_domain(db, domain_in.domain)
    if existing:
        raise HTTPException(status_code=400, detail="Domain already exists")
    try:
        domain = domain_crud.create(db, domain_in)
        return build_api_response(
            request=request,
            result={
                "id": str(domain.id),
                "domain": domain.domain,
                "tenant_id": str(domain.tenant_id),
            },
            status_code=status.HTTP_201_CREATED,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create domain: {e}")


# ----------------------
# List Domains
# ----------------------
@router.get(
    "/",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
)
@request_timer
async def list_domains(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    # dependencies=[Depends(require_permissions(permissions=["domain.list"]))],
    # dependencies=[Depends(require_permissions(["domain.create"]))],
    db: Session = Depends(get_db),
):
    total = domain_crud.count(db)
    domains = domain_crud.get_all(db, skip=skip, limit=limit)
    print(domains)
    data = [
        {
            "id": str(d.id),
            "domain": d.domain,
            "tenant_id": str(d.tenant_id),
            "is_primary": d.is_primary,
            "is_verified": d.is_verified,
        }
        for d in domains
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
        result={"domains": data, **pagination},
        status_code=status.HTTP_200_OK,
    )


# ----------------------
# Get Domain by ID
# ----------------------
@router.get(
    "/{domain_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(require_permissions(permissions=["domain.create"]))],
    # dependencies=[Depends(require_permissions(["domain.create"]))],
)
@request_timer
async def get_domain(
    domain_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    domain = fetch_domain_or_404(domain_id, db)
    return build_api_response(
        request=request,
        include_user_context=False,
        result={
            "id": str(domain.id),
            "domain": domain.domain,
            "tenant_id": str(domain.tenant_id),
            "is_primary": domain.is_primary,
            "is_verified": domain.is_verified,
        },
        status_code=status.HTTP_200_OK,
    )


# ----------------------
# Update Domain
# ----------------------
@router.put(
    "/{domain_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(require_permissions(permissions=["domain.update"]))],
    # dependencies=[Depends(require_permissions(["domain.create"]))],
)
@request_timer
async def update_domain(
    domain_id: str,
    domain_in: DomainUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        domain = fetch_domain_or_404(domain_id, db)
        updated = domain_crud.update(db, domain, domain_in)
        return build_api_response(
            request=request,
            include_user_context=False,
            result={
                "id": str(updated.id),
                "domain": updated.domain,
                "tenant_id": str(updated.tenant_id),
                "is_primary": updated.is_primary,
                "is_verified": updated.is_verified,
                "message": f"Domain '{updated.domain}' updated successfully",
            },
            status_code=status.HTTP_200_OK,
        )
    except Exception as e:
        return build_api_response(
            request=request,
            include_user_context=False,
            result={"error": "InternalServerError", "message": str(e)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ----------------------
# Delete Domain
# ----------------------
@router.delete(
    "/{domain_id}",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(require_permissions(permissions=["domain.create"]))],
    # dependencies=[Depends(require_permissions(["domain.create"]))],
)
@request_timer
async def delete_domain(
    domain_id: str,
    request: Request,
    db: Session = Depends(get_db),
):
    domain = fetch_domain_or_404(domain_id, db)
    try:
        domain_crud.delete(db, domain.id)
        return build_api_response(
            request=request,
            include_user_context=False,
            result={"message": f"Domain '{domain.domain}' deleted successfully"},
            status_code=status.HTTP_200_OK,
        )
    except ValueError as ve:
        return build_api_response(
            request=request,
            include_user_context=False,
            result={"error": str(ve)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except RuntimeError as re:
        return build_api_response(
            request=request,
            include_user_context=False,
            result={"error": str(re)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception:
        return build_api_response(
            request=request,
            include_user_context=False,
            result={"error": "An unexpected error occurred."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
