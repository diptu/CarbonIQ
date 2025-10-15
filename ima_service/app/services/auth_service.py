from __future__ import annotations
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import selectinload

from .base_service import BaseService
from .user_service import UserService
from ..core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from ..core.redis_adapter import RedisAdapter


class AuthService(BaseService[Dict[str, Any]]):
    """
    Authentication service handling:
      - User authentication
      - JWT + Refresh token issuance
      - Token revocation (blacklisting)
      - Optional MFA hooks
      - Brute-force attempt protection
    """

    def __init__(
        self,
        user_service: UserService,
        redis: Optional[RedisAdapter] = None,
        max_login_attempts: int = 5,
        lockout_duration: int = 900,  # 15 minutes
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.user_service = user_service
        self.redis = redis
        self.max_login_attempts = max_login_attempts
        self.lockout_duration = lockout_duration
        self._login_attempts: Dict[str, int] = {}  # fallback if Redis not used

    # -------------------------------------------------------------------------
    # AUTH FLOW
    # -------------------------------------------------------------------------
    async def login(self, email: str, password: str) -> Dict[str, str]:
        """Authenticate user and issue JWT + refresh tokens."""
        # Eager-load roles and permissions
        user = await self.user_service.get_by_email(email)
        if not user:
            await self._record_failed_login(email)
            await self._audit("login_failed", "user", 404, {"email": email})
            raise ValueError("Invalid credentials")

        if await self._is_user_locked(email):
            await self._audit("login_locked", "user", 403, {"email": email})
            raise PermissionError("Account temporarily locked due to failed attempts")

        if not user.verify_password(password):
            await self._record_failed_login(email)
            await self._audit("login_failed", "user", 401, {"email": email})
            raise ValueError("Invalid credentials")

        # Reset failed login on success
        await self._reset_failed_login(email)
        await self._audit("login_success", "user", 200, {"user_id": str(user.id)})

        return await self.issue_tokens(user)

    async def issue_tokens(self, user) -> Dict[str, str]:
        """Generate access and refresh tokens with roles."""
        if not self.tenant_id:
            raise ValueError("Tenant context required for token generation")

        roles: List[str] = [r.name for r in user.roles]

        access_token = create_access_token(
            user_id=str(user.id),  # matches core/security signature
            tenant_id=self.tenant_id,
            roles=roles,
        )
        refresh_token = create_refresh_token(
            user_id=str(user.id),
            tenant_id=self.tenant_id,
        )

        return {"access_token": access_token, "refresh_token": refresh_token}

    async def refresh(self, refresh_token: str) -> Dict[str, str]:
        """Verify refresh token and issue a new access token."""
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user = await self.user_service.get_by_id(payload.get("user_id"))
        if not user:
            raise ValueError("User not found")

        self.tenant_id = payload.get("tenant_id")
        return await self.issue_tokens(user)

    # -------------------------------------------------------------------------
    # TOKEN MANAGEMENT
    # -------------------------------------------------------------------------
    async def revoke_token(self, jti: str, expires_in: int = 3600) -> None:
        if self.redis:
            await self.redis.set_blacklist(jti, expires_in)

    async def is_token_revoked(self, jti: str) -> bool:
        return await self.redis.is_blacklisted(jti) if self.redis else False

    # -------------------------------------------------------------------------
    # SECURITY HELPERS
    # -------------------------------------------------------------------------
    def _check_password_complexity(self, password: str) -> bool:
        return (
            len(password) >= 8
            and any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(not c.isalnum() for c in password)
        )

    async def _record_failed_login(self, email: str) -> None:
        if self.redis:
            key = f"login_attempts:{email}"
            attempts = await self.redis.incr(key)
            if attempts == 1:
                await self.redis.expire(key, self.lockout_duration)
        else:
            self._login_attempts[email] = self._login_attempts.get(email, 0) + 1

    async def _reset_failed_login(self, email: str) -> None:
        if self.redis:
            await self.redis.delete(f"login_attempts:{email}")
        else:
            self._login_attempts.pop(email, None)

    async def _is_user_locked(self, email: str) -> bool:
        if self.redis:
            attempts = await self.redis.get(f"login_attempts:{email}")
            return int(attempts or 0) >= self.max_login_attempts
        return self._login_attempts.get(email, 0) >= self.max_login_attempts

    # -------------------------------------------------------------------------
    # MFA PLACEHOLDERS
    # -------------------------------------------------------------------------
    async def setup_mfa(self, user) -> str:
        return "mfa-secret-placeholder"

    async def verify_mfa(self, user, code: str) -> bool:
        return True
