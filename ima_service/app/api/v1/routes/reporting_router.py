# app/api/v1/routes/reporting_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from app.dependencies.auth import get_current_user, require_permissions
from app.models.user import User

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(require_permissions(["view_reports"]))],
)
async def list_reports(current_user: User = Depends(get_current_user)):
    """List reports (dummy)."""
    return {"total": 0, "items": []}


@router.get(
    "/{report_id}",
    dependencies=[Depends(require_permissions(["view_reports"]))],
)
async def get_report(report_id: UUID, current_user: User = Depends(get_current_user)):
    """Get report by ID (dummy)."""
    return {"report_id": str(report_id), "tenant_id": str(current_user.tenant_id)}
