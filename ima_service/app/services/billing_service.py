# app/services/billing_service.py
"""Tenant-aware billing and subscription service."""

from uuid import UUID
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Example models (you will need to implement these)
from app.models.billing import BillingRecord, Subscription


# ----------------------
# Billing CRUD
# ----------------------
async def create_billing_record(
    db: AsyncSession, tenant_id: UUID, amount: float, description: str
) -> BillingRecord:
    record = BillingRecord(
        tenant_id=tenant_id,
        amount=amount,
        description=description,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def list_billing_records(
    db: AsyncSession, tenant_id: UUID, skip: int = 0, limit: int = 100
) -> List[BillingRecord]:
    result = await db.execute(
        select(BillingRecord)
        .where(BillingRecord.tenant_id == tenant_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# ----------------------
# Subscription Management
# ----------------------
async def get_subscription(db: AsyncSession, tenant_id: UUID) -> Optional[Subscription]:
    result = await db.execute(
        select(Subscription).where(Subscription.tenant_id == tenant_id)
    )
    return result.scalars().first()


async def update_subscription(
    db: AsyncSession, tenant_id: UUID, plan: str, active: bool
) -> Subscription:
    subscription = await get_subscription(db, tenant_id)
    if not subscription:
        subscription = Subscription(tenant_id=tenant_id, plan=plan, active=active)
        db.add(subscription)
    else:
        subscription.plan = plan
        subscription.active = active

    await db.commit()
    await db.refresh(subscription)
    return subscription
