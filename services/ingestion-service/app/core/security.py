"""JWT verification and tenant/RBAC context extraction.

Tokens are issued by auth-service (see services/auth-service and
services/iam-service/README.md for the claim shape). This service never
issues tokens — it only validates them, deny-by-default (zero-trust): every
/api/v1 route requires a valid, non-expired JWT with a tenant_id claim.
"""

from dataclasses import dataclass, field

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class AuthContext:
    """Resolved identity for the current request, extracted from the JWT."""

    user_id: str
    tenant_id: str
    roles: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def decode_token(token: str, settings: Settings) -> dict:
    """Decode + verify a JWT per the configured algorithm.

    RS256 (production): verified against auth-service's public key.
    HS256 (local dev only): verified against a shared secret, so a full
    auth-service isn't required to exercise this service in isolation.
    """
    if settings.jwt_algorithm == "RS256":
        if not settings.jwt_public_key:
            raise _unauthorized("JWT public key is not configured")
        key = settings.jwt_public_key
    else:
        if not settings.jwt_hs256_secret:
            raise _unauthorized("JWT shared secret is not configured")
        key = settings.jwt_hs256_secret

    try:
        return jwt.decode(
            token,
            key=key,
            algorithms=[settings.jwt_algorithm],
            audience=settings.jwt_audience or None,
            issuer=settings.jwt_issuer,
            options={"verify_aud": bool(settings.jwt_audience)},
        )
    except jwt.ExpiredSignatureError as exc:
        raise _unauthorized("Access token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise _unauthorized("Invalid access token") from exc


async def get_current_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> AuthContext:
    """FastAPI dependency: require + parse a bearer JWT into an AuthContext."""
    if credentials is None or not credentials.credentials:
        raise _unauthorized("Missing or invalid Authorization header")

    claims = decode_token(credentials.credentials, settings)

    subject = claims.get("sub")
    tenant_id = claims.get("tenant_id")
    if not subject or not tenant_id:
        raise _unauthorized("Token is missing required sub/tenant_id claims")

    return AuthContext(
        user_id=str(subject),
        tenant_id=str(tenant_id),
        roles=list(claims.get("roles", [])),
        permissions=list(claims.get("permissions", [])),
    )


def require_permission(permission: str):
    """Dependency factory: 403s unless the caller's JWT grants `permission`."""

    async def _checker(auth: AuthContext = Depends(get_current_auth)) -> AuthContext:
        if not auth.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {permission}",
            )
        return auth

    return _checker
