# ruff: noqa: D100
# pylint: disable=missing-function-docstring
"""Tiny logging: color/JSON, uvicorn parity."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

from .settings import Settings, get_settings

_COLORS = {
    logging.DEBUG: "\033[36m",
    logging.INFO: "\033[32m",
    logging.WARNING: "\033[33m",
    logging.ERROR: "\033[31m",
    logging.CRITICAL: "\033[41m",
}
_RESET = "\033[0m"


def _is_tty() -> bool:
    if os.getenv("NO_COLOR"):
        return False
    try:
        return sys.stdout.isatty()
    except OSError:  # pragma: no cover
        return False


class _ColorFmt(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        color = _COLORS.get(record.levelno, "")
        if color:
            record.levelname = f"{color}{record.levelname}{_RESET}"  # type: ignore
        return super().format(record)


class _JsonFmt(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        body = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "pid": os.getpid(),
        }
        known = set(vars(logging.makeLogRecord({})).keys())
        extra = {k: v for k, v in record.__dict__.items() if k not in known}
        if extra:
            body["extra"] = extra
        return json.dumps(body, ensure_ascii=False)


def _handler(level: int, json_mode: bool, color: bool) -> logging.Handler:
    fmt = "%(asctime)s %(levelname)s %(name)s - %(message)s [%(module)s:%(lineno)d]"
    datefmt = "%Y-%m-%dT%H:%M:%S%z"
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(level)
    if json_mode:
        h.setFormatter(_JsonFmt())
    elif color:
        h.setFormatter(_ColorFmt(fmt=fmt, datefmt=datefmt))
    else:
        h.setFormatter(logging.Formatter(fmt=fmt, datefmt=datefmt))
    return h


def _wire_uvicorn(level: int) -> None:
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).setLevel(level)


def configure_logging(settings: Settings | None = None) -> None:
    st = settings or get_settings()
    level = getattr(logging, st.log.level.value)
    json_mode = bool(getattr(st.log, "json_file", None))
    color = bool(st.log.color and not json_mode and _is_tty())

    root = logging.getLogger()
    if not root.handlers:
        root.addHandler(_handler(level, json_mode, color))
    root.setLevel(level)
    for h in root.handlers:
        h.setLevel(level)
    _wire_uvicorn(level)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_success(detail: str, **extra: Any) -> None:
    get_logger("event").info("success: %s", detail, extra=extra)


def log_failure(detail: str, **extra: Any) -> None:
    get_logger("event").error("failure: %s", detail, extra=extra)
