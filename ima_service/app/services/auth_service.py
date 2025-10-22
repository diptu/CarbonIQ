from __future__ import annotations
from typing import Any, Dict, Optional, List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import uuid

from .base_service import BaseService
from .user_service import UserService
from ..core.security import (
    create_access_token,
    create_refresh_token,
    revoke_token,
    validate_refresh_token,
)
from ..schemas.auth_tokens import TokenUser
from app.models.auth_tokens import AuthToken
from app.core.redis_adapter import RedisAdapter
from app.core.exceptions import UnauthorizedException
from app.core.audit_adapter import (
    audit_logger,
    current_user_id,
    current_email,
    current_roles,
    current_permissions,
    current_tenant_id,
)


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

        # ---------------------------
        # Set ContextVars for this user
        # ---------------------------
        current_user_id.set(str(user.id))
        current_email.set(user.email)
        current_roles.set([r.name for r in getattr(user, "roles", [])])
        current_permissions.set(await self.user_service.get_user_permissions(user))
        current_tenant_id.set(self.tenant_id)

        # Audit log successful login
        await audit_logger.log(
            action="login_success", resource="auth", status=200, meta={"email": email}
        )

        return await self.issue_tokens(user)

    async def issue_tokens(self, user) -> Dict[str, Any]:
        roles: list[str] = [r.name for r in getattr(user, "roles", [])]
        permissions: list[str] = await self.user_service.get_user_permissions(user)

        access_token_record = create_access_token(
            user_id=user.id, tenant_id=self.tenant_id, roles=roles
        )
        refresh_token_record = create_refresh_token(user_id=user.id, tenant_id=self.tenant_id)

        self.db.add(refresh_token_record)
        await self.db.commit()
        await self.db.refresh(refresh_token_record)

        token_user = TokenUser(
            id=user.id,
            email=user.email,
            full_name=getattr(user, "full_name", None),
            tenant_id=self.tenant_id,
            roles=roles,
            permissions=permissions,
        )

        token_data = access_token_record.to_token_data(
            user=token_user,
            refresh_token=refresh_token_record.token,
            expires_in=900,
        )

        # Audit log token issuance
        await audit_logger.log(
            action="token_issued",
            resource="auth_token",
            status=200,
            meta={
                "access_token": access_token_record.token[:8] + "...",
                "refresh_token": refresh_token_record.token[:8] + "...",
                "roles": roles,
            },
        )

        return {
            "success": True,
            "data": token_data,
        }

    async def revoke_single_token(self, token: str, db: AsyncSession, user_id: str) -> int:
        token_record = await validate_refresh_token(token, db, tenant_id=None)

        if str(token_record.user_id) != str(user_id):
            raise UnauthorizedException("Cannot revoke token of another user")

        await revoke_token(token_record, db)

        await audit_logger.log(
            action="token_revoked",
            resource="auth_token",
            status=200,
            meta={"token": token[:8] + "..."},
        )

        return 1

    # -------------------------------
    # Rotate refresh token
    # -------------------------------
    async def rotate_refresh_token(self, token_record, db: AsyncSession):
        # Revoke old token
        await revoke_token(token_record, db)

        # Create new refresh token
        new_token = create_refresh_token(
            user_id=token_record.user_id, tenant_id=token_record.tenant_id
        )
        db.add(new_token)
        await db.commit()
        await db.refresh(new_token)
        new_token.last_used_at = datetime.now(timezone.utc)
        await db.commit()
        return new_token

    async def revoke_all_tokens_for_user(
        self,
        user_id: str,
        db: AsyncSession,
        tenant_id: Optional[str] = None,
    ) -> int:
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

        await audit_logger.log(
            action="login_failed",
            resource="auth",
            status=401,
            meta={"email": email, "attempts": self._login_attempts.get(email, 0)},
        )

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
