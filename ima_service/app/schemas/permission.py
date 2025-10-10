# app/schemas/permission.py
from typing import Optional
from pydantic import UUID4, constr
from .base import BaseSchema


class PermissionBase(BaseSchema):
    name: constr(min_length=1, max_length=100)
    description: Optional[constr(max_length=255)] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionRead(PermissionBase):
    id: UUID4
