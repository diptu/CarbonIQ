# ima_service/app/core/errors.py
"""Typed errors for consistent JSON responses (production-ready)."""

from __future__ import annotations

from typing import Any, Mapping, Optional


class AppError(Exception):
    """Domain/HTTP error that serializes cleanly in API responses.

    Attributes:
        status_code: HTTP status code to return.
        code: Short, machine-readable error code (e.g., "FORBIDDEN").
        message: Human-readable description.
        details: Optional structured context for debugging/clients.
    """

    __slots__ = ("status_code", "code", "message", "details")

    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Mapping[str, Any]] = None,
    ) -> None:
        super().__init__(f"{code}: {message}")
        self.status_code = int(status_code)
        self.code = str(code)
        self.message = str(message)
        self.details = dict(details) if details else None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dict payload for the error body."""
        out: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.details is not None:
            out["details"] = self.details
        return out

    def __repr__(self) -> str:  # pragma: no cover
        return (
            "AppError("
            f"status_code={self.status_code}, code={self.code!r}, "
            f"message={self.message!r})"
        )


# ---- Convenience constructors -------------------------------------------------


def bad_request(
    msg: str,
    *,
    code: str = "BAD_REQUEST",
    details: Optional[Mapping[str, Any]] = None,
) -> AppError:
    return AppError(status_code=400, code=code, message=msg, details=details)


def unauthorized(
    msg: str = "Unauthorized",
    *,
    code: str = "UNAUTHORIZED",
    details: Optional[Mapping[str, Any]] = None,
) -> AppError:
    return AppError(status_code=401, code=code, message=msg, details=details)


def forbidden(
    msg: str = "Forbidden",
    *,
    code: str = "FORBIDDEN",
    details: Optional[Mapping[str, Any]] = None,
) -> AppError:
    return AppError(status_code=403, code=code, message=msg, details=details)


def not_found(
    msg: str = "Not found",
    *,
    code: str = "NOT_FOUND",
    details: Optional[Mapping[str, Any]] = None,
) -> AppError:
    return AppError(status_code=404, code=code, message=msg, details=details)


__all__ = ["AppError", "bad_request", "unauthorized", "forbidden", "not_found"]
