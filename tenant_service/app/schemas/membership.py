from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from shared_service.app.models.enums import StatusEnum
from tenant_service.app.models.membership import TenantRole


class TenantMembershipBase(BaseModel):
    """Shared fields for TenantMembership."""

    tenant_id: UUID = Field(..., description="Associated tenant UUID")
    user_id: UUID = Field(..., description="User UUID from User Service")
    tenant_role: TenantRole = Field(
        TenantRole.VIEWER,
        description="Role of the user within the tenant (RBAC level)",
    )
    is_active: StatusEnum = Field(
        StatusEnum.ACTIVE,
        description="Membership active/inactive status",
    )

    class Config:
        use_enum_values = True
        orm_mode = True


class TenantMembershipCreate(TenantMembershipBase):
    """Schema for creating a tenant membership."""

    tenant_role: Optional[TenantRole] = Field(
        TenantRole.MEMBER,
        description="Assign a role to the new member (default: member)",
    )


class TenantMembershipUpdate(BaseModel):
    """Schema for updating tenant membership details."""

    tenant_role: Optional[TenantRole] = None
    is_active: Optional[StatusEnum] = None

    class Config:
        use_enum_values = True
        orm_mode = True


class TenantMembershipRead(TenantMembershipBase):
    """Schema for returning tenant membership details."""

    id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Optional nested tenant info (useful for listing)
    tenant_name: Optional[str] = Field(None, description="Readable tenant name")

    class Config:
        orm_mode = True
