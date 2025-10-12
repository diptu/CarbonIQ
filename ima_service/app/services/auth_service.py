"""Authentication service for IMA Service with secure JWT handling."""

from __future__ import annotations
from typing import Any, Dict

from .base_service import BaseService
from .user_serice import UserService
from ..core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)


class AuthService(BaseService[Dict[str, Any]]):
    """Handles authentication logic, JWT access/refresh tokens, and logout."""

    def __init__(
        self,
        user_service: UserService,
        tenant_id: str,
        actor_id: str,
        db=None,  # Optional, most operations via UserService
    ) -> None:
        super().__init__(db=db, tenant_id=tenant_id, actor_id=actor_id)
        self.user_service = user_service

    async def login(self, credentials: Dict[str, str]) -> Dict[str, Any]:
        """User Login"""
        email = credentials.get("email")
        password = credentials.get("password")
        if not email or not password:
            raise ValueError("Email and password are required")

        user = await self.user_service.get_by_email(email)
        if not user or not verify_password(password, user.password):
            await self._audit(
                action="login_failed",
                resource="user",
                status=401,
                meta={"email": email},
            )
            raise ValueError("Invalid credentials")

        await self._audit(
            action="login_success",
            resource="user",
            status=200,
            meta={"user_id": str(user.id), "email": user.email},
        )

        tenant_id = self.tenant_id
        if not tenant_id:
            raise ValueError("Tenant ID missing for token generation")

        role_names = [r.name for r in user.roles]  # Convert Role objects to str
        access_token = create_access_token(user.id, tenant_id, role_names)
        refresh_token = create_refresh_token(user.id, tenant_id)

        return {
            "user": user.__dict__,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def refresh(self, refresh_token: str) -> Dict[str, str]:
        """Token refresh"""
        payload = verify_token(refresh_token)  # type: ignore
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        email = payload.get("email")
        if not email:
            raise ValueError("Invalid token payload")

        user = await self.user_service.get_by_email(email)
        if not user:
            raise ValueError("User not found")

        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise ValueError("Tenant ID missing for token generation")

        role_names = [r.name for r in user.roles]  # Convert Role objects to str
        new_access_token = create_access_token(user.id, tenant_id, role_names)  # type: ignore
        return {"access_token": new_access_token}

    async def logout(self, user_id: str) -> None:
        """User LOgout"""
        await self._audit(
            action="logout",
            resource="user",
            status=200,
            meta={"user_id": user_id},
        )
