# app/services/registry.py
"""
ServiceRegistry

Centralized dependency injection container for initializing and managing
all service-layer components in the application.

Purpose:
    - Simplifies wiring of services with shared dependencies (e.g., DB session, Redis, RBAC).
    - Ensures consistent use of RBAC, tenant context, and audit logging across services.
    - Provides a single entry point for FastAPI route injection or background tasks.
    - Improves testability by allowing easy substitution of mocks for DB, Redis, or services.

Example usage:

    # Initialize registry with a DB session and optional Redis adapter
    registry = ServiceRegistry(db=db_session, redis=redis_adapter)

    # Access services
    auth_service = registry.auth_service
    user_service = registry.user_service
    billing_service = registry.billing_service

Notes:
    - Services are initialized in the correct dependency order to satisfy RBAC and tenant context.
    - Business services (BillingService, ReportingService) automatically include RBAC checks and audit logging.
"""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.redis_adapter import RedisAdapter
from .rbac_service import RBACService
from .user_service import UserService
from .auth_service import AuthService
from .role_service import RoleService
from .permission_service import PermissionService
from .billing_service import BillingService
from .reporting_service import ReportingService


class ServiceRegistry:
    def __init__(self, db: AsyncSession, redis: Optional[RedisAdapter] = None):
        # RBAC base services
        self.role_service = RoleService(db=db)
        self.permission_service = PermissionService(db=db)
        self.rbac_service = RBACService(
            role_service=self.role_service, permission_crud=self.permission_service
        )
        # Core domain services
        self.user_service = UserService(rbac_service=self.rbac_service, db=db)
        self.auth_service = AuthService(user_service=self.user_service, redis=redis, db=db)
        # Example business services
        self.billing_service = BillingService(rbac_service=self.rbac_service, db=db)
        self.reporting_service = ReportingService(rbac_service=self.rbac_service, db=db)
