# app/core/logger.py
"""Structured JSON and color-coded logging for IMA Service.

Pandas-style docstring
----------------------
Provides production-ready logging with:

- JSON output for structured logging and observability
- Color-coded console output for development
- Optional file logging for audit or error tracking
- Multi-tenant logging support
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from colorama import Fore, Style, init as colorama_init

from app.core.config import get_settings

colorama_init(autoreset=True)
settings = get_settings()

LOG_DIR = Path(settings.AUDIT_LOG_PATH).parent
LOG_DIR.mkdir(parents=True, exist_ok=True)


class JSONFormatter(logging.Formatter):
    """Formats log records as JSON with timestamp, level, and message."""

    def format(self, record: logging.LogRecord) -> str:
        log_record: dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        if hasattr(record, "tenant_id"):
            log_record["tenant_id"] = record.tenant_id
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)


class ColorFormatter(logging.Formatter):
    """Color-coded console output for readability."""

    LEVEL_COLORS: dict[str, str] = {
        "DEBUG": Fore.CYAN,
        "INFO": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CRITICAL": Fore.RED + Style.BRIGHT,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelname, "")
        reset = Style.RESET_ALL
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return f"{color}[{timestamp}] [{record.levelname}] {record.getMessage()}{reset}"


# --- Logger setup --------------------------------------------------
def get_logger(name: str, json_log: bool = False) -> logging.Logger:
    """Return a logger instance with console and file handlers.

    Args
    ----
    name: str
        Logger name
    json_log: bool
        If True, logs are in JSON format (suitable for audit)
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Avoid duplicate handlers
    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(ColorFormatter() if not json_log else JSONFormatter())
        logger.addHandler(ch)

        # File handler
        fh = logging.FileHandler(settings.AUDIT_LOG_PATH)
        fh.setLevel(logging.INFO)
        fh.setFormatter(JSONFormatter())
        logger.addHandler(fh)

    return logger


# --- Convenience loggers ------------------------------------------
audit_logger = get_logger("audit", json_log=True)
app_logger = get_logger("app", json_log=False)
error_logger = get_logger("error", json_log=True)
