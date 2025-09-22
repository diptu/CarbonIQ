"""Users API routes (tenant + RBAC via deps)."""

from __future__ import annotations
from typing import Iterable, List
from fastapi import APIRouter, Depends, Path, Response, status
from ima_service.app.core.errors import AppError
from ima_service.app.domain.services import UserService
from ima_service.app.api.v1.users.deps import (
    get_user_service,
    map_user_to_out,
    owner_only,
    tenant_enforced,
)
from ima_service.app.api.v1.users.schemas import UserCreateIn, UserOut, UserRole
from ima_service.app.api.v1.users.subject import subject_from_claims

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_me(
    sub: str = Depends(subject_from_claims),
    svc: UserService = Depends(get_user_service),
) -> UserOut:
    u = await svc.get_user(sub)
    return (
        map_user_to_out(u) if u else UserOut(id=sub, email=None, role=UserRole.VIEWER)
    )


@router.get("", response_model=List[UserOut], status_code=status.HTTP_200_OK)
async def list_users(
    _c=Depends(tenant_enforced),
    _o=Depends(owner_only),
    svc: UserService = Depends(get_user_service),
) -> list[UserOut]:
    users: Iterable[object] = await svc.list_users()
    return [map_user_to_out(u) for u in users]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreateIn,
    _c=Depends(tenant_enforced),
    _o=Depends(owner_only),
    svc: UserService = Depends(get_user_service),
) -> UserOut:
    created = await svc.create_user(
        email=str(body.email), role=body.role.value, password=body.password
    )
    return map_user_to_out(created)


# NOTE: FastAPI asserts on 204 at route *definition time* if a response class
# with a media type is present. Easiest production-safe workaround:
# - Don't set status_code on the decorator.
# - Return an empty Response(status_code=204) at runtime.
# - Document 204 in the OpenAPI via `responses={204: {...}}`.
@router.delete(
    "/{user_id}",
    responses={204: {"description": "No Content"}},
)
async def delete_user(
    user_id: str = Path(..., min_length=1),
    _c=Depends(tenant_enforced),
    _o=Depends(owner_only),
    svc: UserService = Depends(get_user_service),
) -> Response:
    ok = await svc.delete_user(user_id)
    if not ok:
        raise AppError(
            status_code=404,
            code="USER_NOT_FOUND",
            message="User not found.",
            details={"user_id": user_id},
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
