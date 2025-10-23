# app/core/exceptions.py
"""
Standardized HTTP exceptions for IMA Service.

Features:
- Consistent status codes and messages
- Optional headers
- Extensible base for audit logging integration
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


# ------------------------------
# Base Exception
# ------------------------------
class BaseAPIException(HTTPException):
    """
    Base exception for all IMA Service API errors.

    Parameters
    ----------
    status_code : int
        HTTP status code
    detail : str
        Human-readable error message
    headers : Optional[Dict[str, Any]]
        Optional HTTP headers to include in response
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


# ------------------------------
# 4xx Client Errors
# ------------------------------
class BadRequestException(BaseAPIException):
    """HTTP 400 Bad Request"""

    def __init__(self, detail: str = "Bad Request") -> None:
        super().__init__(status.HTTP_400_BAD_REQUEST, detail)


class UnauthorizedException(BaseAPIException):
    """HTTP 401 Unauthorized"""

    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)


class ForbiddenException(BaseAPIException):
    """HTTP 403 Forbidden"""

    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(status.HTTP_403_FORBIDDEN, detail)


class NotFoundException(BaseAPIException):
    """HTTP 404 Not Found"""

    def __init__(self, detail: str = "Not Found") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class ConflictException(BaseAPIException):
    """HTTP 409 Conflict"""

    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail)


# ------------------------------
# 5xx Server Errors
# ------------------------------
class InternalServerErrorException(BaseAPIException):
    """HTTP 500 Internal Server Error"""

    def __init__(self, detail: str = "Internal Server Error") -> None:
        super().__init__(status.HTTP_500_INTERNAL_SERVER_ERROR, detail)


class ServiceUnavailableException(BaseAPIException):
    """HTTP 503 Service Unavailable"""

    def __init__(self, detail: str = "Service Unavailable") -> None:
        super().__init__(status.HTTP_503_SERVICE_UNAVAILABLE, detail)
