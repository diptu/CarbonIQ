# app/services/billing_service.py
from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.base_service import BaseService
from app.core.config import get_settings

settings = get_settings()


class BillingService(BaseService):
    """
    Lightweight billing helpers for IMA.

    Notes:
    - IMA currently does not have Invoice/Payment models by default.
      Methods attempt to use DB models if present; otherwise they
      return simulated results or raise clear errors suggesting the
      schema additions required.
    - Billing estimates are computed from user counts and a per-user
      rate taken from settings.BILLING_PER_USER (fallback to 1.0).
    """

    def __init__(self, db: AsyncSession):
        super().__init__(db)
        # per-user monthly rate (float) from settings or fallback
        self.per_user_rate: float = getattr(settings, "BILLING_PER_USER", 1.0)

    async def get_tenant_plan(self, tenant_id: UUID) -> Dict[str, Any]:
        """
        Return billing plan info for tenant. If tenant model has a
        'plan' attribute it will be returned, otherwise return a
        best-effort default plan dictionary.
        """
        from app.models.tenants import Tenant  # type: ignore

        stmt = select(Tenant).where(Tenant.id == tenant_id)
        res = await self.db.execute(stmt)
        tenant = res.scalar_one_or_none()
        if not tenant:
            raise ValueError("Tenant not found")

        plan = getattr(tenant, "plan", None)
        if plan:
            return {"tenant_id": str(tenant_id), "plan": plan}

        # Fallback default plan
        return {"tenant_id": str(tenant_id), "plan": "basic"}

    async def estimate_monthly_charge(self, tenant_id: UUID) -> float:
        """
        Estimate monthly charge for a tenant based on active users and
        per-user rate. If User model absent, raise informative error.
        """
        try:
            from app.models.user import User  # type: ignore

            stmt = (
                select(func.count())
                .select_from(User)
                .where(User.tenant_id == tenant_id, User.is_active == True)
            )
            res = await self.db.execute(stmt)
            active_users = int(res.scalar() or 0)
            return float(active_users) * float(self.per_user_rate)
        except Exception as e:
            # If user model missing or DB error, provide helpful message.
            raise RuntimeError(
                f"Cannot compute billing estimate: user model missing or DB error ({e})"
            )

    async def create_invoice_stub(
        self, tenant_id: UUID, amount: float, metadata: Optional[dict] = None
    ) -> Dict[str, Any]:
        """
        If an Invoice model exists, persist and return it. Otherwise,
        return a simulated invoice dict. This lets the service be used
        in code paths before full billing models exist.
        """
        try:
            from app.models.invoice import Invoice  # type: ignore

            invoice = Invoice(
                tenant_id=tenant_id,
                amount=amount,
                status="pending",
                metadata=metadata or {},
            )
            self.db.add(invoice)
            await self.db.commit()
            await self.db.refresh(invoice)
            return {"invoice_db": True, "id": str(invoice.id), "amount": float(amount)}
        except Exception:
            # No Invoice model → return a simulated invoice for testing.
            return {
                "invoice_db": False,
                "id": f"sim-{tenant_id}-{int(amount * 100)}",
                "amount": float(amount),
                "status": "pending",
                "metadata": metadata or {},
            }

    async def total_due_amount(self, tenant_id: UUID) -> float:
        """
        Compute total pending due amount. If Invoice model present,
        sum pending invoices; otherwise raise NotImplementedError.
        """
        try:
            from app.models.invoice import Invoice  # type: ignore

            stmt = select(func.coalesce(func.sum(Invoice.amount), 0)).where(
                Invoice.tenant_id == tenant_id, Invoice.status == "pending"
            )
            res = await self.db.execute(stmt)
            return float(res.scalar() or 0.0)
        except Exception:
            raise NotImplementedError(
                "Invoice model not available. Add billing models to use "
                "total_due_amount."
            )
