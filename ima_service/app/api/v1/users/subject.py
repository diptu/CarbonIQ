"""Helpers to extract subject (user id) from claims for users endpoints.

This module uses package-qualified imports (ima_service.app...) so it works
consistently when the service is run as the `ima_service` package.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import Depends
from ima_service.app.core.security import Claims, current_claims


def subject_from_claims(claims: Claims = Depends(current_claims)) -> str:
    """Return subject (sub) from verified access token claims.

    Raises an AppError via the dependency chain if token is invalid; here we
    just ensure a string return for downstream code.
    """
    sub = claims.get("sub")
    if sub is None:
        # current_claims should have already raised, but be defensive
        raise RuntimeError("token missing subject")
    return str(sub)
