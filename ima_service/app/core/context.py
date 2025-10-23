# app/core/context.py
"""
Async-safe request & user context management.

Provides ContextVars for per-request state including:
- user identity
- tenant
- roles/permissions
- tracing: trace_id and correlation_id
"""

from __future__ import annotations
from contextvars import ContextVar, Token
from typing import List, Optional, Tuple
from fastapi import Request
from uuid import uuid4

# ------------------------------
# Context Variables
# ------------------------------
current_user_id: ContextVar[Optional[str]] = ContextVar("current_user_id", default=None)
current_email: ContextVar[Optional[str]] = ContextVar("current_email", default=None)
current_roles: ContextVar[List[str]] = ContextVar("current_roles", default=[])
current_permissions: ContextVar[List[str]] = ContextVar("current_permissions", default=[])
current_tenant_id: ContextVar[Optional[str]] = ContextVar("current_tenant_id", default=None)
current_trace_id: ContextVar[Optional[str]] = ContextVar("current_trace_id", default=None)
current_correlation_id: ContextVar[Optional[str]] = ContextVar(
    "current_correlation_id", default=None
)


# ------------------------------
# Public helpers
# ------------------------------
def init_trace_ids(
    trace_id: Optional[str] = None, correlation_id: Optional[str] = None
) -> Tuple[str, str]:
    """
    Initialize or return existing trace_id and correlation_id.

    Returns:
        Tuple of (trace_id, correlation_id)
    """
    trace_id = trace_id or f"req_{uuid4().hex}"
    correlation_id = correlation_id or f"corr_{uuid4().hex}"

    current_trace_id.set(trace_id)
    current_correlation_id.set(correlation_id)

    return trace_id, correlation_id


async def set_request_context(request: Request) -> None:
    """
    Populate context variables from FastAPI Request object.
    Use inside middleware or endpoint dependency.
    """
    init_trace_ids()

    current_user_id.set(getattr(request.state, "user_id", None))
    current_email.set(getattr(request.state, "email", None))
    current_roles.set(getattr(request.state, "roles", []))
    current_permissions.set(getattr(request.state, "permissions", []))
    current_tenant_id.set(getattr(request.state, "tenant_id", None))


def reset_context() -> None:
    """
    Reset all context variables to defaults.
    Useful for testing or long-lived async tasks.
    """
    current_user_id.set(None)
    current_email.set(None)
    current_roles.set([])
    current_permissions.set([])
    current_tenant_id.set(None)
    current_trace_id.set(None)
    current_correlation_id.set(None)


# ------------------------------
# Context getters
# ------------------------------
def get_user_id() -> Optional[str]:
    return current_user_id.get()


def get_email() -> Optional[str]:
    return current_email.get()


def get_roles() -> List[str]:
    return current_roles.get()


def get_permissions() -> List[str]:
    return current_permissions.get()


def get_tenant_id() -> Optional[str]:
    return current_tenant_id.get()


def get_trace_id() -> Optional[str]:
    return current_trace_id.get()


def get_correlation_id() -> Optional[str]:
    return current_correlation_id.get()
