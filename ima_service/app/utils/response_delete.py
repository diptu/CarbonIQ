"""Standardized API response utilities.

Ensures all responses follow a consistent JSON envelope:
- status_code: HTTP status code
- msg: short message
- details: response payload (optional)
- pagination: metadata for paginated results
"""

from typing import Any, Optional, TypedDict


class Pagination(TypedDict, total=False):
    """Pagination metadata for paginated API responses."""

    total: Optional[int]
    nextPage: Optional[int]
    prevPage: Optional[int]


class APIResponse(TypedDict, total=False):
    """Standardized API response envelope."""

    status_code: int
    msg: str
    details: Any
    pagination: Pagination


def success_response(  # pylint: disable=R0913
    msg: str,
    details: Any = None,
    status_code: int = 200,
    *,
    total: Optional[int] = None,
    next_page: Optional[int] = None,
    prev_page: Optional[int] = None,
) -> APIResponse:
    """Format a standardized success API response."""
    response: APIResponse = {
        "status_code": status_code,
        "msg": msg,
    }

    if details is not None:
        response["details"] = details

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
) -> APIResponse:
    """Format a standardized error API response."""
    response: APIResponse = {
        "status_code": status_code,
        "msg": msg,
    }

    if details is not None:
        response["details"] = details

    return response
