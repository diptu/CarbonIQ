# app/schemas/role.py
from typing import Optional
from pydantic import UUID4, constr
from .base import BaseSchema


class RoleBase(BaseSchema):
    name: constr(min_length=1, max_length=50)
    description: Optional[constr(max_length=255)] = None
    is_system: bool = False


class RoleCreate(RoleBase):
    pass


class RoleRead(RoleBase):
    id: UUID4


class RoleUpdate(BaseSchema):
    description: Optional[constr(max_length=255)] = None
