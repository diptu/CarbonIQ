# ruff: noqa: D100
"""Core re-exports (minimal to avoid duplicate-code with app/__init__)."""

from __future__ import annotations

from .errors import AppError, register_exception_handlers
from .logging import configure_logging, get_logger
from .settings import get_settings

__version__ = "0.1.0"
