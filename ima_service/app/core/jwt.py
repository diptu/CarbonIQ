from datetime import datetime, timedelta
from typing import List
from uuid import UUID
import jwt
from app.core.config import get_settings

settings = get_settings()


def create_access_token(
    user_id: UUID,
    tenant_id: UUID,
    roles: List[str],
    expires_minutes: int | None = None,
) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: UUID,
    tenant_id: UUID,
    roles: List[str],
    expires_days: int | None = None,
) -> str:
    expire = datetime.utcnow() + timedelta(
        days=expires_days or settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "user_id": str(user_id),
        "tenant_id": str(tenant_id),
        "roles": roles,
        "exp": expire,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode JWT token (access or refresh) and verify claims."""
    return jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
    )
