from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from enum import Enum


# ----------------------
# Role Enum
# ----------------------
class RoleName(str, Enum):
    BILLING_ADMIN = "BILLING_ADMIN"
    TENANT_ADMIN = "TENANT_ADMIN"
    VIEWER = "VIEWER"
    MEMBER = "MEMBER"


# ----------------------
# Base Role fields
# ----------------------
class RoleBase(BaseModel):
    name: RoleName
    description: Optional[str] = None


# ----------------------
# Role creation schema
# ----------------------
class RoleCreate(RoleBase):
    pass  # Inherits name and description from RoleBase


# ----------------------
# Role read schema
# ----------------------
class RoleRead(RoleBase):
    id: UUID  # <-- Use UUID instead of int

    model_config = {
        "from_attributes": True  # Pydantic v2 ORM conversion
    }
