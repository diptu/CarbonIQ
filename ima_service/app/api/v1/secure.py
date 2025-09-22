"""Small secured endpoints to demo RBAC & tenant enforcement."""

from __future__ import annotations
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from ima_service.app.core.security import (
    Claims,
    current_claims,
    enforce_tenant_header_match,
    require_roles,
)

router = APIRouter(prefix="/secure", tags=["secure"])


class Pong(BaseModel):
    status: str = "ok"
    sub: str
    role: str | None = None
    tenant: str | None = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "ok", "sub": "u-0001", "role": "owner", "tenant": "acme"}
            ]
        }
    }


@router.get("/ping", response_model=Pong, status_code=status.HTTP_200_OK)
async def ping(claims: Claims = Depends(enforce_tenant_header_match)) -> Pong:
    """Any authenticated user; if token has tenant, header must match."""
    return Pong(
        sub=str(claims["sub"]), role=claims.get("role"), tenant=claims.get("tenant")
    )


@router.get("/owner", response_model=Pong, status_code=status.HTTP_200_OK)
async def owner_only(claims: Claims = Depends(require_roles(["owner"]))) -> Pong:
    """Owner-only route."""
    return Pong(
        sub=str(claims["sub"]), role=claims.get("role"), tenant=claims.get("tenant")
    )


@router.get("/editor-or-owner", response_model=Pong, status_code=status.HTTP_200_OK)
async def editor_or_owner(
    claims: Claims = Depends(require_roles(["owner", "editor"])),
) -> Pong:
    """Editors and Owners can reach here."""
    return Pong(
        sub=str(claims["sub"]), role=claims.get("role"), tenant=claims.get("tenant")
    )
