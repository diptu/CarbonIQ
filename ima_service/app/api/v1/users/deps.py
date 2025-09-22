"""Users API deps (service wiring, guards, mappers; compact, prod-ready)."""

from __future__ import annotations
from fastapi import Depends
from ima_service.app.core.security import (
    Claims,
    enforce_tenant_header_match,
    require_roles,
)
from ima_service.app.domain.services import PasswordHasher, UserRepo, UserService
from .schemas import UserOut, UserRole

_SERVICE = UserService(UserRepo(), PasswordHasher())
_ROLE_VALUES = {r.value for r in UserRole}


def _role_norm(v: object) -> UserRole:
    try:
        s = str(v)
        return UserRole(s) if s in _ROLE_VALUES else UserRole.VIEWER
    except Exception:
        return UserRole.VIEWER


async def get_user_service() -> UserService:
    return _SERVICE


async def tenant_enforced(
    claims: Claims = Depends(enforce_tenant_header_match),
) -> Claims:
    return claims


async def owner_only(
    claims: Claims = Depends(require_roles([UserRole.Owner.value])),
) -> Claims:
    return claims


def map_user_to_out(u: object) -> UserOut:
    if isinstance(u, dict):
        return UserOut(
            id=str(u.get("id", "")),
            email=u.get("email"),
            role=_role_norm(u.get("role")),
        )
    return UserOut(
        id=str(getattr(u, "id", "")),
        email=getattr(u, "email", None),
        role=_role_norm(getattr(u, "role", None)),
    )


__all__ = ["get_user_service", "tenant_enforced", "owner_only", "map_user_to_out"]
