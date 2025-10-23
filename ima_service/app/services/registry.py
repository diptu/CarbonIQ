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

# app/services/registry.py
from typing import Optional, Dict
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
    """
    A+ grade Service Registry with lazy initialization, dependency injection,
    tenant-aware context, Redis integration, and testability support.
    """

    def __init__(self, db: AsyncSession, redis: Optional[RedisAdapter] = None):
        self.db: AsyncSession = db
        self.redis: Optional[RedisAdapter] = redis

        # Internal storage for lazy services
        self._services: Dict[str, object] = {}

        # Initialize base services eagerly
        self.role_service: RoleService = RoleService(db=db)
        self.permission_service: PermissionService = PermissionService(db=db)

        # Initialize RBAC service eagerly
        self.rbac_service: RBACService = RBACService(
            role_service=self.role_service, permission_crud=self.permission_service
        )

    # ------------------------
    # Lazy-loaded services
    # ------------------------
    @property
    def user_service(self) -> UserService:
        if "user_service" not in self._services:
            self._services["user_service"] = UserService(rbac_service=self.rbac_service, db=self.db)
        return self._services["user_service"]

    @property
    def auth_service(self) -> AuthService:
        if "auth_service" not in self._services:
            self._services["auth_service"] = AuthService(
                user_service=self.user_service, redis=self.redis, db=self.db
            )
        return self._services["auth_service"]

    @property
    def billing_service(self) -> BillingService:
        if "billing_service" not in self._services:
            self._services["billing_service"] = BillingService(
                rbac_service=self.rbac_service, db=self.db
            )
        return self._services["billing_service"]

    @property
    def reporting_service(self) -> ReportingService:
        if "reporting_service" not in self._services:
            self._services["reporting_service"] = ReportingService(
                rbac_service=self.rbac_service, db=self.db
            )
        return self._services["reporting_service"]

    # ------------------------
    # Health Checks
    # ------------------------
    async def health_check(self) -> dict:
        """
        Perform basic health checks for DB and Redis.
        Returns:
            dict: Status summary.
        """
        status = {"db": "ok", "redis": "ok"}

        try:
            # Simple DB check
            await self.db.execute("SELECT 1")
        except Exception:
            status["db"] = "fail"

        if self.redis:
            try:
                await self.redis.ping()
            except Exception:
                status["redis"] = "fail"

        return status

    # ------------------------
    # Utility: clear lazy services
    # ------------------------
    def reset_services(self) -> None:
        """
        Clears all lazy-loaded services (useful for testing).
        """
        self._services.clear()
