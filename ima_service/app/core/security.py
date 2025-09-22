"""JWT helpers + FastAPI deps (iss/aud/nbf/leeway, kid rotation, RBAC, tenant)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, Literal, Optional, Sequence, Tuple, cast
from uuid import uuid4

import jwt  # PyJWT
from fastapi import Depends, Header, status
from fastapi.security import OAuth2PasswordBearer

from .errors import AppError
from .settings import Settings, get_settings

TokenKind = Literal["access", "refresh"]
Claims = Dict[str, Any]

_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# --------------------------------------------------------------------------- #
# Key management (HS* family, simple rotation via kid -> secret mapping)
# --------------------------------------------------------------------------- #


def _select_sign_key(st: Settings) -> Tuple[str, Optional[str]]:
    """Return (secret, kid) for signing. Prefers configured rotating keys."""
    kid = st.jwt.current_kid
    if kid and kid in st.jwt.keys:
        return st.jwt.keys[kid].get_secret_value(), kid
    # fallback: legacy single secret (no kid header)
    return st.jwt.secret_key.get_secret_value(), None


def _resolve_verify_key(token: str, st: Settings) -> str:
    """Pick verification key based on header.kid when provided."""
    try:
        hdr = jwt.get_unverified_header(token) or {}
    except jwt.InvalidTokenError as e:
        raise AppError(
            status_code=401, code="TOKEN_MALFORMED", message="Malformed token header."
        ) from e
    kid = hdr.get("kid")
    if kid is not None:
        secret = st.jwt.keys.get(str(kid))
        if not secret:
            raise AppError(
                status_code=401, code="KID_UNKNOWN", message="Unknown token key id."
            )
        return secret.get_secret_value()
    # no kid → use legacy single secret
    return st.jwt.secret_key.get_secret_value()


# --------------------------------------------------------------------------- #
# Encode / decode
# --------------------------------------------------------------------------- #


def _encode(payload: Dict[str, Any], st: Settings) -> str:
    secret, kid = _select_sign_key(st)
    headers = {"kid": kid} if kid else None
    return cast(
        str,
        jwt.encode(payload, secret, algorithm=st.jwt.algorithm, headers=headers),
    )


def _decode(token: str, st: Settings) -> Claims:
    key = _resolve_verify_key(token, st)
    verify_aud = bool(st.jwt.audience)
    verify_iss = bool(st.jwt.issuer)
    try:
        return cast(
            Claims,
            jwt.decode(
                token,
                key,
                algorithms=[st.jwt.algorithm],
                audience=st.jwt.audience if verify_aud else None,
                issuer=st.jwt.issuer if verify_iss else None,
                leeway=st.jwt.leeway_seconds,
                options={
                    "require": ["exp", "iat", "typ", "nbf"],
                    "verify_aud": verify_aud,
                    "verify_iss": verify_iss,
                },
            ),
        )
    except jwt.ExpiredSignatureError as e:
        raise AppError(
            status_code=401, code="TOKEN_EXPIRED", message="Token expired."
        ) from e
    except jwt.InvalidAudienceError as e:
        raise AppError(
            status_code=401, code="TOKEN_AUDIENCE", message="Invalid audience."
        ) from e
    except jwt.InvalidIssuerError as e:
        raise AppError(
            status_code=401, code="TOKEN_ISSUER", message="Invalid issuer."
        ) from e
    except jwt.ImmatureSignatureError as e:
        raise AppError(
            status_code=401, code="TOKEN_NOT_YET_VALID", message="Token not yet valid."
        ) from e
    except jwt.InvalidTokenError as e:
        raise AppError(
            status_code=401, code="TOKEN_INVALID", message="Invalid token."
        ) from e


def _make_token(
    *, kind: TokenKind, payload: Dict[str, Any], st: Settings, ttl: timedelta
) -> str:
    now = datetime.now(timezone.utc)
    body: Dict[str, Any] = {
        "typ": kind,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
    }
    if st.jwt.issuer:
        body["iss"] = st.jwt.issuer
    if st.jwt.audience:
        body["aud"] = st.jwt.audience
    if kind == "refresh" and "jti" not in payload:
        body["jti"] = uuid4().hex
    return _encode({**body, **payload}, st)


def create_access_token(
    payload: Dict[str, Any],
    st: Optional[Settings] = None,
    expires: Optional[timedelta] = None,
) -> str:
    s = st or get_settings()
    ttl = expires or timedelta(minutes=s.jwt.access_expire_minutes)
    return _make_token(kind="access", payload=payload, st=s, ttl=ttl)


def create_refresh_token(
    payload: Dict[str, Any],
    st: Optional[Settings] = None,
    expires: Optional[timedelta] = None,
) -> str:
    s = st or get_settings()
    ttl = expires or timedelta(days=s.jwt.refresh_expire_days)
    return _make_token(kind="refresh", payload=payload, st=s, ttl=ttl)


def verify_token(
    token: str, expected: TokenKind = "access", st: Optional[Settings] = None
) -> Claims:
    s = st or get_settings()
    claims = _decode(token, s)
    if claims.get("typ") != expected:
        raise AppError(
            status_code=401, code="TOKEN_WRONG_TYPE", message="Wrong token type."
        )
    if expected == "refresh" and "jti" not in claims:
        raise AppError(
            status_code=401,
            code="REFRESH_JTI_MISSING",
            message="Refresh token missing JTI.",
        )
    return claims


def get_jti(claims: Claims) -> str | None:
    j = claims.get("jti")
    return str(j) if j is not None else None


def get_tenant(claims: Claims) -> str | None:
    t = claims.get("tenant")
    return str(t) if t is not None else None


# --------------------------------------------------------------------------- #
# FastAPI dependencies
# --------------------------------------------------------------------------- #


async def current_claims(token: str = Depends(_oauth2)) -> Claims:
    return verify_token(token, expected="access")


def require_roles(allowed: Optional[Sequence[str]] = None):
    """RBAC gate. Example: Depends(require_roles(['owner','editor']))."""
    allowed_set = set(allowed or ())

    async def _dep(claims: Claims = Depends(current_claims)) -> Claims:
        role = claims.get("role")
        if allowed_set and role not in allowed_set:
            raise AppError(
                status_code=403,
                code="FORBIDDEN",
                message="Forbidden.",
                details={"role": role, "allowed": sorted(allowed_set)},
            )
        return claims

    return _dep


async def enforce_tenant_header_match(
    claims: Claims = Depends(current_claims),
    tenant_header: str | None = Header(None, alias="X-Tenant-ID"),
) -> Claims:
    """If token has a tenant claim, require matching X-Tenant-ID header."""
    token_tenant = get_tenant(claims)
    if token_tenant:
        if not tenant_header:
            raise AppError(
                status_code=400,
                code="TENANT_HEADER_REQUIRED",
                message="Missing X-Tenant-ID header.",
            )
        if tenant_header != token_tenant:
            raise AppError(
                status_code=403,
                code="TENANT_MISMATCH",
                message="Tenant mismatch.",
                details={"token_tenant": token_tenant, "header": tenant_header},
            )
    return claims


__all__ = [
    "Claims",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "get_jti",
    "get_tenant",
    "current_claims",
    "require_roles",
    "enforce_tenant_header_match",
]
