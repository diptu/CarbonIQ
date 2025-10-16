from __future__ import annotations
from typing import Any, Dict, Optional, List
from fastapi import HTTPException, status
from .base_service import BaseService
from .user_service import UserService
from ..core.security import verify_password, create_access_token, create_refresh_token
from ..core.redis_adapter import RedisAdapter
from datetime import datetime, timezone
import uuid


class AuthService(BaseService[Dict[str, Any]]):
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
        self._login_attempts: Dict[str, int] = {}

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        # Fetch user ignoring tenant for super-user login
        user = await self.user_service.get_by_email(email, ignore_tenant=True)

        if not user:
            await self._record_failed_login(email)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        is_super_user = getattr(user, "is_super_user", False)

        # Tenant validation
        if self.tenant_id:
            if not is_super_user and not self.can_login_to_tenant(user.tenant_id, self.tenant_id):
                await self._record_failed_login(email)
                raise HTTPException(
                    status_code=403,
                    detail=f"Tenant '{self.tenant_id}' does not exist or access denied",
                )
        else:
            if not is_super_user:
                await self._record_failed_login(email)
                raise HTTPException(
                    status_code=403,
                    detail="Tenant access denied: header 'x-tenant-id' required for non-super-users",
                )

        if not user.is_active:
            await self._record_failed_login(email)
            raise HTTPException(status_code=403, detail="User is inactive")

        if await self._is_user_locked(email):
            raise HTTPException(status_code=403, detail="Account temporarily locked")

        if not user.verify_password(password):
            await self._record_failed_login(email)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        await self._reset_failed_login(email)
        return await self.issue_tokens(user)

    async def issue_tokens(self, user) -> Dict[str, Any]:
        roles: list[str] = [r.name for r in getattr(user, "roles", [])]
        permissions: list[str] = await self.user_service.get_user_permissions(user)

        access_token = create_access_token(
            user_id=str(user.id), tenant_id=self.tenant_id, roles=roles
        )
        refresh_token = create_refresh_token(user_id=str(user.id), tenant_id=self.tenant_id)

        return {
            "success": True,
            "data": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": 900,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": getattr(user, "full_name", None),
                    "tenant_id": getattr(user, "tenant_id", None),
                    "roles": roles,
                    "permissions": permissions,
                },
            },
            "meta": {
                "request_id": f"req_{str(uuid.uuid4())[:8]}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

    def can_login_to_tenant(self, user_tenant: Optional[str], login_tenant: str) -> bool:
        if not user_tenant:
            return False
        return user_tenant == login_tenant or login_tenant.endswith(f".{user_tenant}")

    # -----------------------------
    # Redis login attempt helpers
    # -----------------------------
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
