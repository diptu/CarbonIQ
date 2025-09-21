# ima_service/app/__init__.py
"""Application package: core, domain, persistence, and API wiring."""

from __future__ import annotations

# pylint: disable=invalid-name
__version__ = "0.1.0"

from app.core import (  # noqa: F401
    AppError,
    configure_logging,
    get_logger,
    get_settings,
    register_exception_handlers,
)

__all__ = [
    "__version__",
    "get_settings",
    "configure_logging",
    "get_logger",
    "AppError",
    "register_exception_handlers",
]
