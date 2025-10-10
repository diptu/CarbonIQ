# app/services/base_service.py
"""Base service class with structured logging, audit, error handling, and tenant context.

Pandas-style docstring
----------------------
Provides a foundational service class with:

- DB session management
- Tenant context propagation
- RBAC enforcement scaffolding
- Decorator-based structured logging for CRUD
- Audit logging for critical DB changes
- Error logging for exceptions
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Generic, TypeVar
from sqlalchemy.orm import Session
from app.models.base_class import Base
from app.dependencies.rbac import check_permission
from app.core.logger import app_logger, audit_logger, error_logger

T = TypeVar("T", bound=Base)
F = TypeVar("F", bound=Callable[..., Any])
# Add this to app/services/base_service.py


def log_action(
    event_name: str, metadata: dict[str, any], tenant_id: str | None = None
) -> None:
    """Log a structured action event to audit logger.

    Args
    ----
    event_name: str
        Name of the action/event (e.g., 'create_user')
    metadata: dict
        Relevant key/value data about the action
    tenant_id: str | None
        Tenant context for multi-tenant logging
    """
    audit_logger.info(
        {
            "event": event_name,
            "metadata": metadata,
            "tenant": tenant_id,
        }
    )


def log_method_call(func: F) -> F:
    """Decorator to log method calls with arguments, results, and exceptions."""

    @wraps(func)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        tenant_id = getattr(self, "tenant_id", None)
        try:
            # Log start of method call
            app_logger.info(
                {
                    "event": "method_call",
                    "method": func.__name__,
                    "args": args,
                    "kwargs": kwargs,
                    "tenant": tenant_id,
                }
            )

            result = func(self, *args, **kwargs)

            # Audit logging for critical DB actions
            if func.__name__ in ("add", "delete", "update"):
                audit_logger.info(
                    {
                        "event": func.__name__,
                        "args": args,
                        "kwargs": kwargs,
                        "result": str(result),
                        "tenant": tenant_id,
                    }
                )

            # Log return
            app_logger.info(
                {
                    "event": "method_return",
                    "method": func.__name__,
                    "result": str(result),
                    "tenant": tenant_id,
                }
            )

            return result
        except Exception as e:
            # Log structured error
            error_logger.exception(
                {
                    "event": "method_exception",
                    "method": func.__name__,
                    "args": args,
                    "kwargs": kwargs,
                    "tenant": tenant_id,
                    "exception": str(e),
                }
            )
            raise

    return wrapper  # type: ignore[return-value]


class BaseService(Generic[T]):
    """Generic base service for DB models with tenant-aware operations."""

    def __init__(self, db: Session, tenant_id: str | None = None) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def has_permission(self, user_id: str, permission_name: str) -> bool:
        """Check if the user has permission for this action in tenant context."""
        if not self.tenant_id:
            raise ValueError("Tenant context not set for service.")
        return check_permission(
            db=self.db,
            user_id=user_id,
            permission_name=permission_name,
            tenant_id=self.tenant_id,
        )

    @log_method_call
    def add(self, obj: T) -> T:
        """Add and commit a model instance to the DB."""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    @log_method_call
    def delete(self, obj: T) -> None:
        """Delete a model instance from the DB."""
        self.db.delete(obj)
        self.db.commit()

    @log_method_call
    def update(self, obj: T, **kwargs: Any) -> T:
        """Update a model instance with given attributes."""
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    @log_method_call
    def get(self, model_cls: type[T], obj_id: str) -> T | None:
        """Fetch a model instance by ID within the tenant context."""
        return (
            self.db.query(model_cls)
            .filter(model_cls.id == obj_id, model_cls.tenant_id == self.tenant_id)
            .first()
        )

    @log_method_call
    def list(self, model_cls: type[T], **filters: Any) -> list[T]:
        """List model instances with optional filters and tenant scoping."""
        query = self.db.query(model_cls).filter(model_cls.tenant_id == self.tenant_id)
        for attr, value in filters.items():
            query = query.filter(getattr(model_cls, attr) == value)
        return query.all()
