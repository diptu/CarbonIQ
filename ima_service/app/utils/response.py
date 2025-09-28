# app/utils/response.py
"""Standardized API response utilities.

Ensures all responses follow a consistent JSON envelope:
- status_code: HTTP status code
- msg: short message
- details: response payload (optional)
- pagination: metadata for paginated results
"""

from typing import Any, Optional


def success_response(
    msg: str,
    details: Any = None,
    status_code: int = 200,
    total: Optional[int] = None,
    next_page: Optional[int] = None,
    prev_page: Optional[int] = None,
) -> dict[str, Any]:
    """Format a success response."""
    response: dict[str, Any] = {
        "status_code": status_code,
        "msg": msg,
    }

    if details is not None:
        response["details"] = details

    # only include pagination if relevant
    if total is not None or next_page is not None or prev_page is not None:
        response["pagination"] = {
            "total": total,
            "nextPage": next_page,
            "prevPage": prev_page,
        }

    return response


def error_response(
    msg: str,
    status_code: int,
    details: Any = None,
) -> dict[str, Any]:
    """Format an error response."""
    response: dict[str, Any] = {
        "status_code": status_code,
        "msg": msg,
    }
    if details is not None:
        response["details"] = details
    return response
