# # app/api/v1/routes/billing_router.py
# from fastapi import APIRouter, Depends, HTTPException, status
# from typing import List
# from uuid import UUID

# from app.dependencies.auth import get_current_user, require_permissions
# from app.models.user import User

# router = APIRouter()


# @router.post(
#     "/",
#     status_code=status.HTTP_201_CREATED,
#     dependencies=[Depends(require_permissions(["manage_billing"]))],
# )
# async def create_billing(current_user: User = Depends(get_current_user)):
#     """Create a new billing record (dummy, no DB)."""
#     return {"msg": f"Billing created for tenant {current_user.tenant_id}"}


# @router.get(
#     "/",
#     dependencies=[Depends(require_permissions(["view_billing"]))],
# )
# async def list_billings(current_user: User = Depends(get_current_user)):
#     """List billing records (dummy)."""
#     return {"total": 0, "items": []}


# @router.get(
#     "/{billing_id}",
#     dependencies=[Depends(require_permissions(["view_billing"]))],
# )
# async def get_billing(billing_id: UUID, current_user: User = Depends(get_current_user)):
#     """Get billing record by ID (dummy)."""
#     return {"billing_id": str(billing_id), "tenant_id": str(current_user.tenant_id)}


# @router.delete(
#     "/{billing_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
#     dependencies=[Depends(require_permissions(["manage_billing"]))],
# )
# async def delete_billing(
#     billing_id: UUID, current_user: User = Depends(get_current_user)
# ):
#     """Delete billing record by ID (dummy)."""
#     return {"msg": f"Billing {billing_id} deleted"}
