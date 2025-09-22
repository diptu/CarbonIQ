"""Auth endpoints: login (rate-limited), refresh (rotation), logout (RBAC/tenant)."""

from __future__ import annotations
from inspect import isawaitable
from types import SimpleNamespace
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from ...core.errors import AppError
from ...core.ratelimit import enforce_login_limits
from ...core.security import (
    Claims,
    create_access_token,
    create_refresh_token,
    get_jti,
    verify_token,
)
from ...core.settings import Settings, get_settings
from ...core.token_store import TokenStore, get_token_store, ttl_from_exp

# Use real authenticator if present; fallback to demo for bootstrap.
try:
    from ...domain.services import authenticate_user  # type: ignore[attr-defined]
except Exception:  # pragma: no cover

    def authenticate_user(email: str, password: str):  # type: ignore[misc]
        return (
            SimpleNamespace(id="u-demo-owner", role="owner")
            if (email.lower() == "admin@example.com" and password == "secret")
            else None
        )


router = APIRouter(prefix="/auth", tags=["auth"])


class TokenPair(BaseModel):
    access_token: str = Field(..., description="JWT access token (Bearer)")
    refresh_token: str = Field(..., description="JWT refresh token (rotation-enabled)")
    token_type: str = Field("bearer", description="Always 'bearer'")
    expires_in: int = Field(..., description="Access token TTL (seconds)")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "<access.jwt>",
                    "refresh_token": "<refresh.jwt>",
                    "token_type": "bearer",
                    "expires_in": 900,
                }
            ]
        }
    }


class RefreshIn(BaseModel):
    refresh_token: str = Field(..., examples=["<refresh.jwt>"])


class LogoutIn(BaseModel):
    refresh_token: Optional[str] = Field(None, examples=["<refresh.jwt>"])
    all: bool = Field(False, description="Revoke all sessions for this user")


def _obj_get(o: Any, k: str, d: Any = None) -> Any:
    return o.get(k, d) if isinstance(o, dict) else getattr(o, k, d)


def _access_ttl_seconds(st: Settings) -> int:
    return int(st.jwt.access_expire_minutes) * 60


@router.post(
    "/login",
    response_model=TokenPair,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Invalid credentials"},
        429: {"description": "Too many attempts"},
    },
)
async def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    st: Settings = Depends(get_settings),
    store: TokenStore = Depends(get_token_store),
    tenant: str | None = Header(None, alias="X-Tenant-ID"),
) -> TokenPair:
    """OAuth2 password login; binds tenant if X-Tenant-ID provided; rate-limited."""
    # Soft rate-limit: if Redis is unavailable, we do NOT block login.
    try:
        await enforce_login_limits(request=request, username=form.username)
    except AppError:
        raise
    except Exception:  # pragma: no cover - limiter fallback
        pass

    maybe = authenticate_user(form.username, form.password)  # type: ignore
    user = await maybe if isawaitable(maybe) else maybe
    if not user:
        raise AppError(
            status_code=401, code="INVALID_CREDENTIALS", message="Invalid credentials."
        )
    user_id = str(_obj_get(user, "id"))
    if not user_id:
        raise AppError(
            status_code=500, code="USER_ID_MISSING", message="User record missing 'id'."
        )

    role = str(_obj_get(user, "role", "viewer"))
    claims: Dict[str, Any] = {"sub": user_id, "role": role}
    if tenant:
        claims["tenant"] = tenant

    access = create_access_token(claims, st=st)
    refresh = create_refresh_token(claims, st=st)
    r_claims = verify_token(refresh, expected="refresh", st=st)
    jti = get_jti(r_claims)
    if not jti:
        raise AppError(
            status_code=500,
            code="REFRESH_JTI_MISSING",
            message="Refresh token missing JTI.",
        )
    await store.mark_refresh_active(
        user_id=user_id, jti=jti, ttl_s=ttl_from_exp(int(r_claims["exp"]))
    )
    return TokenPair(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        expires_in=_access_ttl_seconds(st),
    )


@router.post(
    "/refresh",
    response_model=TokenPair,
    responses={401: {"description": "Invalid/expired refresh or reuse detected"}},
)
async def refresh(
    body: RefreshIn,
    st: Settings = Depends(get_settings),
    store: TokenStore = Depends(get_token_store),
) -> TokenPair:
    """Rotate refresh and mint a new access token; detects reuse and revokes all."""
    r = verify_token(body.refresh_token, expected="refresh", st=st)
    user_id = str(r["sub"])
    old_jti = get_jti(r)
    if not old_jti:
        raise AppError(
            status_code=401,
            code="REFRESH_JTI_MISSING",
            message="Invalid refresh token.",
        )
    if not await store.is_refresh_active(old_jti):
        await store.revoke_all_for_user(user_id)
        raise AppError(
            status_code=401,
            code="REFRESH_REUSED",
            message="Refresh token reuse detected. All sessions revoked.",
        )
    claims: Dict[str, Any] = {"sub": user_id, "role": str(r.get("role", "viewer"))}
    if "tenant" in r:
        claims["tenant"] = str(r["tenant"])
    access = create_access_token(claims, st=st)
    new_refresh = create_refresh_token(claims, st=st)
    nr = verify_token(new_refresh, expected="refresh", st=st)
    new_jti = get_jti(nr)
    if not new_jti:
        raise AppError(
            status_code=500,
            code="REFRESH_JTI_MISSING",
            message="New refresh token missing JTI.",
        )
    await store.rotate_refresh(
        user_id=user_id,
        old_jti=old_jti,
        new_jti=new_jti,
        ttl_s=ttl_from_exp(int(nr["exp"])),
    )
    return TokenPair(
        access_token=access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=_access_ttl_seconds(st),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    responses={
        204: {"description": "No Content"},
        400: {"description": "refresh_token required"},
    },
)
async def logout(
    body: LogoutIn,
    st: Settings = Depends(get_settings),
    store: TokenStore = Depends(get_token_store),
) -> Response:
    """Logout current session or all sessions (requires refresh token)."""
    if not body.refresh_token:
        raise AppError(
            status_code=400,
            code="REFRESH_REQUIRED",
            message="refresh_token is required.",
        )
    r = verify_token(body.refresh_token, expected="refresh", st=st)
    user_id = str(r["sub"])
    jti = get_jti(r)
    if body.all:
        await store.revoke_all_for_user(user_id)
        return Response(status_code=204)
    if not jti:
        raise AppError(
            status_code=400,
            code="REFRESH_JTI_MISSING",
            message="Invalid refresh token.",
        )
    await store.revoke_refresh(jti, user_id=user_id)
    return Response(status_code=204)
