# app/core/exceptions.py
"""Custom exceptions for authentication, authorization, and RBAC.

Pandas-style docstring
----------------------
This module defines structured exceptions for the IMA service:

- HTTP exceptions for API responses
- Custom RBAC, tenant, and authentication errors
- Provides reusable functions for raising exceptions consistently
"""

from fastapi import HTTPException, status


# --- Authentication Exceptions -----------------------------------
def raise_invalid_credentials() -> None:
    """Raise HTTP 401 for invalid username/password."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def raise_inactive_user() -> None:
    """Raise HTTP 403 for inactive user login attempts."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Inactive user",
    )


def raise_invalid_token() -> None:
    """Raise HTTP 401 for invalid or expired JWT token."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )


# --- Authorization / RBAC Exceptions -----------------------------
def raise_permission_denied() -> None:
    """Raise HTTP 403 when user lacks required permission."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied",
    )


def raise_role_assignment_denied() -> None:
    """Raise HTTP 403 when user tries to assign roles outside scope."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Role assignment not allowed",
    )


# --- Tenant / Multi-tenancy Exceptions --------------------------
def raise_tenant_access_denied() -> None:
    """Raise HTTP 403 when user tries to access another tenant."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Tenant access denied",
    )


def raise_tenant_not_found() -> None:
    """Raise HTTP 404 when tenant does not exist."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Tenant not found",
    )


# --- Resource Exceptions ----------------------------------------
def raise_resource_not_found(resource_name: str = "Resource") -> None:
    """Raise HTTP 404 when a resource is not found."""
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"{resource_name} not found",
    )


def raise_resource_conflict(resource_name: str = "Resource") -> None:
    """Raise HTTP 409 when a resource conflicts (e.g., duplicate entry)."""
    raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=f"{resource_name} already exists",
    )
