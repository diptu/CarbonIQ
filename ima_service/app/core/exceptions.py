"""
app/core/exception.py
---------------------
Custom exception classes for the IMA Service.

These provide standardized HTTPException wrappers with default messages and
status codes for consistent API error handling.

Notes
-----
- Inherit from BaseHTTPException for all service-specific errors.
- Extend with domain-specific exceptions if needed (e.g., ValidationError).
- Compatible with FastAPI exception handlers and DRF-style responses.
"""

from __future__ import annotations

from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    """Base class for all custom HTTP exceptions in the IMA Service."""

    def __init__(self, *, status_code: int, detail: str, headers: dict | None = None):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UnauthorizedException(BaseHTTPException):
    """401 Unauthorized — Authentication credentials are missing or invalid."""

    def __init__(self, detail: str = "Unauthorized"):
        super().__init(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(BaseHTTPException):
    """403 Forbidden — Authenticated but not authorized to perform this action."""

    def __init__(self, detail: str = "Forbidden"):
        super().__init(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(BaseHTTPException):
    """404 Not Found — The requested resource does not exist."""

    def __init__(self, detail: str = "Not Found"):
        super().__init(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(BaseHTTPException):
    """400 Bad Request — The request parameters are invalid."""

    def __init__(self, detail: str = "Bad Request"):
        super().__init(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(BaseHTTPException):
    """409 Conflict — The request could not be completed due to a conflict."""

    def __init__(self, detail: str = "Conflict"):
        super().__init(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InternalServerErrorException(BaseHTTPException):
    """500 Internal Server Error — An unexpected error occurred."""

    def __init__(self, detail: str = "Internal server error"):
        super().__init(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
