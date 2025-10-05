# app/services/reporting_service.py
"""Tenant-aware reporting service."""

from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Example model (replace with actual models)
from app.models.billing import BillingRecord
from app.models.user import User


# ----------------------
# Tenant Billing Report
# ----------------------
async def generate_billing_report(
    db: AsyncSession, tenant_id: UUID
) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(BillingRecord).where(BillingRecord.tenant_id == tenant_id)
    )
    records = result.scalars().all()
    report = [
        {"amount": r.amount, "description": r.description, "created_at": r.created_at}
        for r in records
    ]
    return report


# ----------------------
# Tenant User Activity Report
# ----------------------
async def generate_user_report(
    db: AsyncSession, tenant_id: UUID
) -> List[Dict[str, Any]]:
    result = await db.execute(select(User).where(User.tenant_id == tenant_id))
    users = result.scalars().all()
    report = [
        {
            "email": u.email,
            "is_active": u.is_active,
            "roles": [role.name for role in u.roles],
            "created_at": u.created_at,
        }
        for u in users
    ]
    return report
