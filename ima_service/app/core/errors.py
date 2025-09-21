# ima_service/app/core/errors.py
"""Minimal typed errors + FastAPI handlers with uniform JSON shape."""

from __future__ import annotations

from typing import Any, Dict, Optional, cast

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .logging import get_logger

log = get_logger(__name__)


class AppError(Exception):
    """Domain error with HTTP status and stable code."""

    def __init__(
        self,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def _body(
    *,
    status_str: str,
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Uniform JSON body for all errors."""
    body: Dict[str, Any] = {"status": status_str, "code": code, "message": message}
    if details:
        body["details"] = details
    return body


async def _on_app_error(_: Request, exc: Exception) -> JSONResponse:
    """Handle AppError uniformly."""
    err = cast(AppError, exc)
    log.warning("app error: %s (%s)", err.message, err.code, extra=err.details)
    return JSONResponse(
        status_code=err.status_code,
        content=_body(
            status_str="error",
            code=err.code,
            message=err.message,
            details=err.details,
        ),
    )


async def _on_http(_: Request, exc: Exception) -> JSONResponse:
    """Normalize FastAPI HTTPException to our JSON shape."""
    http_exc = cast(HTTPException, exc)
    msg = str(http_exc.detail) if http_exc.detail else "HTTP error"
    log.info("http error: %s", msg, extra={"code": "http.error"})
    return JSONResponse(
        status_code=http_exc.status_code,
        content=_body(status_str="error", code="http.error", message=msg),
    )


async def _on_validation(_: Request, exc: Exception) -> JSONResponse:
    """Handle FastAPI/Pydantic validation errors."""
    val_exc = cast(RequestValidationError | ValidationError, exc)
    errs = val_exc.errors()
    log.debug("validation error", extra={"errors": errs})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_body(
            status_str="fail",
            code="validation.error",
            message="Validation failed.",
            details={"errors": errs},
        ),
    )


async def _on_unexpected(_: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions."""
    log.exception("unexpected error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_body(
            status_str="error",
            code="internal.error",
            message="Internal server error.",
        ),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach exception handlers to the FastAPI app."""
    app.add_exception_handler(AppError, _on_app_error)
    app.add_exception_handler(HTTPException, _on_http)
    app.add_exception_handler(RequestValidationError, _on_validation)
    app.add_exception_handler(ValidationError, _on_validation)
    app.add_exception_handler(Exception, _on_unexpected)
