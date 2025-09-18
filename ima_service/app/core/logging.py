# FILE: ima_service/app/core/logging.py
"""
Structured logging (JSON) with optional ANSI color for console.

- Dev (DEBUG=True): colorized JSON to stderr.
- Prod (DEBUG=False): plain JSON (console and/or file).
- Unifies stdlib + Uvicorn under one JSON envelope.
- Import-safe; only mutates handlers in setup_logging().

Usage
-----
from ima_service.app.core.logging import setup_logging
setup_logging(debug=settings.debug)
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Final, Mapping, MutableMapping

# -----------------------------
# ANSI colors
# -----------------------------
LEVEL_COLORS: Final[Mapping[int, str]] = {
    logging.DEBUG: "\x1b[38;5;244m",  # gray
    logging.INFO: "\x1b[38;5;39m",  # blue
    logging.WARNING: "\x1b[38;5;214m",  # orange
    logging.ERROR: "\x1b[38;5;196m",  # red
    logging.CRITICAL: "\x1b[48;5;196m\x1b[97m",  # red bg + white fg
}
RESET: Final[str] = "\x1b[0m"

_STD_ATTRS: Final[set[str]] = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}


def _iso_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _coerce(obj: Any) -> Any:
    """Best-effort JSON coercion for arbitrary objects."""
    try:
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):  # pragma: no cover
        # Narrow exceptions to avoid broad-exception-caught (W0718)
        return repr(obj)


def _extras(record: logging.LogRecord) -> dict[str, Any]:
    """Collect non-standard LogRecord attributes into a dict."""
    out: dict[str, Any] = {}
    for k, v in record.__dict__.items():
        if k not in _STD_ATTRS and not k.startswith("_"):
            out[k] = _coerce(v)
    return out


class _JSONFormatter(logging.Formatter):
    """Single JSON formatter; optional colorization for console."""

    def __init__(self, *, color: bool = False, is_access: bool = False) -> None:
        super().__init__()
        self.color = color
        self.is_access = is_access  # uvicorn.access flavor

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        payload: MutableMapping[str, Any] = {
            "ts": _iso_utc_now(),
            "level": record.levelname,
            "logger": record.name if not self.is_access else "uvicorn.access",
            "message": record.getMessage(),
        }

        if not self.is_access:
            payload.update(
                {
                    "module": record.module,
                    "func": record.funcName,
                    "line": record.lineno,
                }
            )
        else:
            # Known uvicorn access extras if present
            for key in ("client_addr", "request_line", "status_code"):
                if hasattr(record, key):
                    payload[key] = getattr(record, key)

        extras = _extras(record)
        if extras:
            payload["extra"] = extras

        if record.exc_info and not self.is_access:
            payload["exc_info"] = self.formatException(record.exc_info)

        if self.color:
            color = LEVEL_COLORS.get(record.levelno)
            if color:
                payload["level"] = f"{color}{payload['level']}{RESET}"

        return json.dumps(payload, ensure_ascii=False)


def _build_handlers(*, debug: bool, json_file: str | None) -> list[logging.Handler]:
    console = logging.StreamHandler(stream=sys.stderr)
    console.setLevel(logging.DEBUG if debug else logging.INFO)
    console.setFormatter(_JSONFormatter(color=debug, is_access=False))
    handlers: list[logging.Handler] = [console]

    file_path = json_file or os.environ.get("LOG_JSON_FILE")
    if file_path:
        fh = logging.FileHandler(file_path, encoding="utf-8")
        fh.setLevel(logging.DEBUG if debug else logging.INFO)
        fh.setFormatter(_JSONFormatter(color=False, is_access=False))
        handlers.append(fh)

    return handlers


def setup_logging(
    *,
    debug: bool = False,
    json_file: str | None = None,
    include_uvicorn: bool = True,
) -> None:
    """
    Configure structured logging.

    Parameters
    ----------
    debug
        Colorized JSON to console when True; else plain JSON.
    json_file
        Optional path to write plain JSON logs (in addition to console).
    include_uvicorn
        If True, route Uvicorn loggers through the same JSON format.
    """
    handlers = _build_handlers(debug=debug, json_file=json_file)

    # Root logger
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.DEBUG if debug else logging.INFO)
    for h in handlers:
        root.addHandler(h)
    root.propagate = False

    # Quiet noisy libs (tune as needed)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)

    if include_uvicorn:
        # uvicorn.error mirrors root handlers
        uvicorn_error = logging.getLogger("uvicorn.error")
        uvicorn_error.handlers.clear()
        for h in handlers:
            uvicorn_error.addHandler(h)
        uvicorn_error.setLevel(logging.DEBUG if debug else logging.INFO)
        uvicorn_error.propagate = False

        # uvicorn.access uses access-style formatter (console + optional file)
        access_handlers: list[logging.Handler] = []
        access_console = logging.StreamHandler(stream=sys.stderr)
        access_console.setLevel(logging.INFO)
        access_console.setFormatter(_JSONFormatter(color=False, is_access=True))
        access_handlers.append(access_console)

        file_path = json_file or os.environ.get("LOG_JSON_FILE")
        if file_path:
            access_file = logging.FileHandler(file_path, encoding="utf-8")
            access_file.setLevel(logging.INFO)
            access_file.setFormatter(_JSONFormatter(color=False, is_access=True))
            access_handlers.append(access_file)

        uvicorn_access = logging.getLogger("uvicorn.access")
        uvicorn_access.handlers.clear()
        for h in access_handlers:
            uvicorn_access.addHandler(h)
        uvicorn_access.setLevel(logging.INFO)
        uvicorn_access.propagate = False
