from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Union
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.auth_tokens import AuthToken
from app.core.config import get_settings
from app.core.exceptions import (
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
)
from app.services.audit_adapter import AuditAdapter

# Initialize
settings = get_settings()
audit_logger = AuditAdapter()

SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS: int = settings.REFRESH_TOKEN_EXPIRE_DAYS


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# 🔐 TOKEN CREATION
# ---------------------------------------------------------------------------


def create_access_token(
    *,
    user_id: Union[str, UUID],
    tenant_id: Union[str, UUID],
    roles: List[str],
    expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
) -> AuthToken:
    """Create a signed JWT access token."""
    now = _utcnow()
    expire = now + timedelta(minutes=expires_minutes)
    payload = {
        "sub": str(user_id),
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "type": "access",
        "iat": now,
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }

    token_str = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return AuthToken(
        user_id=user_id,
        token=token_str,
        jti=str(uuid4()),
        issued_at=now,
        expires_at=expire,
        token_type="access",
        revoked=False,
        tenant_id=tenant_id,
        last_used_at=None,
    )


def create_refresh_token(
    *, user_id: Union[str, UUID], tenant_id: Union[str, UUID], expires_days: Optional[int] = None
) -> AuthToken:
    """Create a signed JWT refresh token."""
    now = _utcnow()
    expire = now + timedelta(days=expires_days or REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "type": "refresh",
        "iat": now,
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
    }

    token_str = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return AuthToken(
        user_id=user_id,
        token=token_str,
        jti=str(uuid4()),
        issued_at=now,
        expires_at=expire,
        token_type="refresh",
        revoked=False,
        tenant_id=tenant_id,
        last_used_at=None,
    )


# ---------------------------------------------------------------------------
# ✅ VALIDATION
# ---------------------------------------------------------------------------


async def validate_refresh_token(
    token_str: str,
    db: AsyncSession,
    tenant_id: Optional[str] = None,  # optional now
) -> AuthToken:
    """
    Validate a refresh token:
    - Decode & verify JWT
    - Ensure it exists, not expired, not revoked
    - Optionally ensure tenant ownership matches
    Raises:
        UnauthorizedException (401)
        ForbiddenException (403)
    """
    try:
        payload = jwt.decode(
            token_str,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
    except ExpiredSignatureError:
        await audit_logger.log(
            action="token_validate",
            resource="refresh_token",
            status=401,
            meta={"reason": "expired"},
        )
        raise UnauthorizedException("Refresh token has expired")
    except JWTError as e:
        await audit_logger.log(
            action="token_validate",
            resource="refresh_token",
            status=401,
            meta={"reason": f"invalid_jwt: {e}"},
        )
        raise UnauthorizedException("Invalid refresh token")

    # Fetch from DB
    result = await db.execute(select(AuthToken).where(AuthToken.token == token_str))
    token_record: Optional[AuthToken] = result.scalar_one_or_none()

    if not token_record:
        await audit_logger.log(
            action="token_validate",
            resource="refresh_token",
            status=401,
            meta={"reason": "not_found"},
        )
        raise NotFoundException("Refresh token not found")

    # Tenant ownership check (optional)
    if tenant_id is not None and token_record.tenant_id != tenant_id:
        await audit_logger.log(
            action="token_validate",
            resource="refresh_token",
            status=403,
            meta={"reason": "wrong_tenant"},
        )
        raise ForbiddenException("Refresh token from wrong tenant")

    # Expiration check
    if token_record.expires_at and token_record.expires_at < datetime.now(timezone.utc):
        await audit_logger.log(
            action="token_validate",
            resource="refresh_token",
            status=401,
            meta={"reason": "expired_db"},
        )
        raise UnauthorizedException("Refresh token has expired")

    # Revocation check
    if token_record.revoked:
        await audit_logger.log(
            action="token_validate",
            resource="refresh_token",
            status=401,
            meta={"reason": "revoked"},
        )
        raise UnauthorizedException("Refresh token has been revoked")

    await audit_logger.log(
        action="token_validate",
        resource="refresh_token",
        status=200,
        meta={"result": "success", "tenant_id": token_record.tenant_id},
    )

    return token_record


# ---------------------------------------------------------------------------
# 🚫 REVOCATION
# ---------------------------------------------------------------------------


async def revoke_token(token: AuthToken, db: AsyncSession):
    """Mark a token as revoked and log the event."""
    token.revoked = True
    token.revoked_at = _utcnow()
    await db.commit()

    await audit_logger.log(
        action="token_revoke",
        resource="auth_token",
        status=200,
        meta={
            "token_type": token.token_type,
            "tenant_id": str(token.tenant_id),
            "user_id": str(token.user_id),
            "jti": token.jti,
        },
    )


def verify_token(token_str: str) -> dict:
    """
    Decode and validate an access token (JWT).
    Raises UnauthorizedException if invalid or expired.
    Returns the decoded payload if valid.
    """
    try:
        payload = jwt.decode(
            token_str,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        if payload.get("type") != "access":
            raise UnauthorizedException("Token is not an access token")
        return payload
    except ExpiredSignatureError:
        raise UnauthorizedException("Access token has expired")
    except JWTError as e:
        raise UnauthorizedException(f"Invalid access token: {e}")
