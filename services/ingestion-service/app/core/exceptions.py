"""Exception handlers that translate errors into the standard envelope."""

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.responses import error_envelope

logger = logging.getLogger("ingestion_service")

_STATUS_CODES = {
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_403_FORBIDDEN: "forbidden",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: "payload_too_large",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "validation_error",
}


def _code_for_status(status_code: int) -> str:
    return _STATUS_CODES.get(status_code, "error")


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=error_envelope(_code_for_status(exc.status_code), str(exc.detail)),
        headers=exc.headers,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    first_error = exc.errors()[0] if exc.errors() else {}
    field = ".".join(str(p) for p in first_error.get("loc", []) if p != "body")
    message = first_error.get("msg", "Validation error")
    detail = f"{field}: {message}" if field else message
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_envelope("validation_error", detail),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error while processing %s %s", request.method, request.url)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_envelope("internal_error", "An unexpected error occurred"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
