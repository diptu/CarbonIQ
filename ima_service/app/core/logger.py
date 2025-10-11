"""Centralized logging configuration for IMA Service.

Pandas-style docstring
----------------------
This module sets up a production-ready logger with console, file,
and rotating file support. Log level is environment-configurable.

Notes
-----
- Uses `get_settings()` to load audit log path and debug mode.
- RotatingFileHandler prevents unbounded log file growth.
- Compatible with structured logging if needed.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import get_settings

settings = get_settings()

LOG_DIR = Path(settings.AUDIT_LOG_PATH).parent
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Determine log level
LOG_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO

# Formatter
FORMATTER = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

# -----------------------------
# Root logger
# -----------------------------
logger = logging.getLogger("carboniq")
logger.setLevel(LOG_LEVEL)
logger.propagate = False  # Avoid double logging if used in other modules

# -----------------------------
# Console handler
# -----------------------------
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(FORMATTER)
logger.addHandler(console_handler)

# -----------------------------
# File handler (rotating)
# -----------------------------
file_handler = RotatingFileHandler(
    filename=settings.AUDIT_LOG_PATH,
    mode="a",
    maxBytes=10 * 1024 * 1024,  # 10 MB per file
    backupCount=5,  # keep last 5 logs
    encoding="utf-8",
    delay=False,
)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(FORMATTER)
logger.addHandler(file_handler)

# -----------------------------
# Convenience short-hands
# -----------------------------
debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical
exception = logger.exception
