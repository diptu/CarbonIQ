# ruff: noqa: D100
"""Tiny JWT helpers + FastAPI deps."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal, Optional, Sequence, cast

import jwt  # type: ignore[import-not-found]  # pylint: disable=import-error
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer

from .errors import AppError
from .settings import Settings, get_settings

TokenKind = Literal["access", "refresh"]
Claims = Dict[str, Any]
_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def _encode(payload: Dict[str, Any], st: Settings) -> str:
    """Encode a payload with HMAC."""
    token = jwt.encode(
        payload, st.jwt.secret_key.get_secret_value(), algorithm=st.jwt.algorithm
    )
    return cast(str, token)


def _decode(token: str, st: Settings) -> Claims:
    """Decode a JWT and validate required claims."""
    try:
        return jwt.decode(
            token,
            st.jwt.secret_key.get_secret_value(),
            algorithms=[st.jwt.algorithm],
            options={"require": ["exp", "iat", "typ"]},
        )
    except jwt.ExpiredSignatureError as exc:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="TOKEN_EXPIRED",
            message="Token expired.",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="TOKEN_INVALID",
            message="Invalid token.",
        ) from exc


def _make_token(
    *, kind: TokenKind, payload: Dict[str, Any], st: Optional[Settings], ttl: timedelta
) -> str:
    """Create a signed JWT of the given kind."""
    s = st or get_settings()
    now = datetime.now(timezone.utc)
    body = {
        "typ": kind,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
    }
    return _encode({**body, **payload}, s)


def create_access_token(
    payload: Dict[str, Any],
    st: Optional[Settings] = None,
    expires: Optional[timedelta] = None,
) -> str:
    """Short-lived access token."""
    s = st or get_settings()
    ttl = expires or timedelta(minutes=s.jwt.access_expire_minutes)
    return _make_token(kind="access", payload=payload, st=s, ttl=ttl)


def create_refresh_token(
    payload: Dict[str, Any],
    st: Optional[Settings] = None,
    expires: Optional[timedelta] = None,
) -> str:
    """Long-lived refresh token."""
    s = st or get_settings()
    ttl = expires or timedelta(days=s.jwt.refresh_expire_days)
    return _make_token(kind="refresh", payload=payload, st=s, ttl=ttl)


def verify_token(
    token: str, expected: TokenKind = "access", st: Optional[Settings] = None
) -> Claims:
    """Verify token and enforce expected kind."""
    s = st or get_settings()
    claims = _decode(token, s)
    if claims.get("typ") != expected:
        raise AppError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="TOKEN_WRONG_TYPE",
            message="Wrong token type.",
        )
    return claims


async def current_claims(token: str = Depends(_oauth2)) -> Claims:
    """Dep: return verified access claims."""
    return verify_token(token, expected="access")


def require_roles(allowed: Optional[Sequence[str]] = None):
    """Dep: ensure user's role in allowed set."""
    allowed_set = set(allowed or ())

    async def _dep(claims: Claims = Depends(current_claims)) -> Claims:
        role = claims.get("role")
        if allowed_set and role not in allowed_set:
            raise AppError(
                status_code=status.HTTP_403_FORBIDDEN,
                code="FORBIDDEN",
                message="Forbidden.",
                details={"role": role, "allowed": sorted(allowed_set)},
            )
        return claims

    return _dep
