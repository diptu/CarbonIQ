# app/schemas/tenant.py
from pydantic import UUID4, constr
from typing import Optional
from .base import BaseSchema


class TenantBase(BaseSchema):
    name: constr(min_length=1, max_length=100)
    domain: constr(min_length=3, max_length=255)
    schema_name: constr(min_length=3, max_length=100)
    parent_id: Optional[UUID4] = None


class TenantCreate(TenantBase):
    pass


class TenantRead(TenantBase):
    id: UUID4


class TenantUpdate(BaseSchema):
    name: Optional[constr(min_length=1, max_length=100)] = None
    domain: Optional[constr(min_length=3, max_length=255)] = None
