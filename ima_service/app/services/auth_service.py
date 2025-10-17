# app/services/auth_service.py
from __future__ import annotations
from typing import Any, Dict, Optional, List
from fastapi import HTTPException
from .base_service import BaseService
from .user_service import UserService
from ..core.security import (
    create_access_token,
    create_refresh_token,
    revoke_token,
    validate_refresh_token,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..schemas.auth_tokens import TokenUser
from app.models.auth_tokens import AuthToken
from ..core.redis_adapter import RedisAdapter
from app.core.exceptions import UnauthorizedException
from datetime import datetime, timezone
import uuid
from app.services.audit_adapter import AuditAdapter

audit_logger = AuditAdapter()


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
        user = await self.user_service.get_by_email(email, ignore_tenant=True)
        if not user:
            await self._record_failed_login(email)
            raise HTTPException(status_code=401, detail="Invalid credentials")

        is_super_user = getattr(user, "is_super_user", False)

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

        # 1️⃣ Create JWT tokens (returns AuthToken objects)
        access_token_record = create_access_token(
            user_id=user.id, tenant_id=self.tenant_id, roles=roles
        )
        refresh_token_record = create_refresh_token(user_id=user.id, tenant_id=self.tenant_id)

        # 2️⃣ Store refresh token in DB
        self.db.add(refresh_token_record)
        await self.db.commit()
        await self.db.refresh(refresh_token_record)

        # 3️⃣ Prepare user object for response
        token_user = TokenUser(
            id=user.id,
            email=user.email,
            full_name=getattr(user, "full_name", None),
            tenant_id=self.tenant_id,
            roles=roles,
            permissions=permissions,
        )

        # 4️⃣ Convert AuthToken objects to TokenData
        token_data = access_token_record.to_token_data(
            user=token_user,
            refresh_token=refresh_token_record.token,
            expires_in=900,
        )

        return {
            "success": True,
            "data": token_data,
            "meta": {
                "request_id": f"req_{str(uuid.uuid4())[:8]}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

    async def revoke_single_token(self, token: str, db: AsyncSession, user_id: str) -> int:
        """
        Revoke a single refresh token. Skips tenant check.
        Ensures the token belongs to the given user.
        """
        token_record = await validate_refresh_token(token, db, tenant_id=None)  # skip tenant check

        # Ensure token belongs to current user
        if str(token_record.user_id) != str(user_id):
            raise UnauthorizedException("Cannot revoke token of another user")

        await revoke_token(token_record, db)
        return 1

    async def revoke_all_tokens_for_user(
        self,
        user_id: str,
        db: AsyncSession,
        tenant_id: Optional[str] = None,  # <--- make it optional
    ) -> int:
        """Revoke all refresh tokens for a user (optionally filtered by tenant)."""
        query = select(AuthToken).where(
            AuthToken.user_id == user_id,
            AuthToken.token_type == "refresh",
            AuthToken.revoked == False,
        )

        if tenant_id:
            query = query.where(AuthToken.tenant_id == tenant_id)

        result = await db.execute(query)
        tokens: List[AuthToken] = result.scalars().all()

        revoked_count = 0
        for token in tokens:
            token.revoked = True
            token.revoked_at = datetime.now(timezone.utc)
            revoked_count += 1

        if revoked_count > 0:
            await db.commit()
            await audit_logger.log(
                action="logout",
                resource="auth_token",
                status=200,
                actor_id=user_id,
                tenant_id=tenant_id,
                meta={"revoked_count": revoked_count},
            )

        return revoked_count

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
