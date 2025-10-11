"""Custom exceptions for IMA Service.

Pandas-style docstring
----------------------
This module defines standardized HTTPException wrappers for FastAPI
to ensure consistent status codes and error responses across the service.

Notes
-----
- All exceptions inherit from FastAPI's HTTPException.
- Optional `detail` message can be customized.
- Optional `headers` allow passing custom HTTP headers if needed.
"""

from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class BaseAPIException(HTTPException):
    """Base exception for all IMA Service API errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the exception.

        Parameters
        ----------
        status_code : int
            HTTP status code.
        detail : str
            Human-readable error message.
        headers : Optional[Dict[str, Any]]
            Optional HTTP headers to include in response.
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UnauthorizedException(BaseAPIException):
    """401 Unauthorized"""

    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(BaseAPIException):
    """403 Forbidden"""

    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(BaseAPIException):
    """404 Not Found"""

    def __init__(self, detail: str = "Not Found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(BaseAPIException):
    """400 Bad Request"""

    def __init__(self, detail: str = "Bad Request") -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(BaseAPIException):
    """409 Conflict"""

    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
