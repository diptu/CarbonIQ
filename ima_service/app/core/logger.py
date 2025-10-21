from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json
from typing import Optional, Any, Dict
from .config import get_settings

settings = get_settings()
LOG_DIR = Path(settings.AUDIT_LOG_PATH).parent
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO
SERVICE_NAME = getattr(settings, "SERVICE_NAME", "ima_service")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "service": SERVICE_NAME,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record)


logger = logging.getLogger("carboniq")
logger.setLevel(LOG_LEVEL)
logger.propagate = False

formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z")

# Console
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Rotating file
file_handler = RotatingFileHandler(
    filename=settings.AUDIT_LOG_PATH,
    mode="a",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
file_handler.setLevel(LOG_LEVEL)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_audit_level(action: Optional[str], status: int = 0) -> int:
    action = (action or "").lower()
    if 200 <= status < 300:
        return logging.INFO
    if 400 <= status < 500:
        return logging.WARNING
    if 500 <= status < 600:
        return logging.ERROR
    if action.endswith("_success"):
        return logging.INFO
    if action.endswith("_attempt"):
        return logging.WARNING
    if action.endswith(("_failed", "_forbidden", "_internal_error")):
        return logging.ERROR
    if action.endswith("_debug"):
        return logging.DEBUG
    return logging.INFO
