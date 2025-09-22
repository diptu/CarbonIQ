"""Color console logging + optional JSON file sink (failsafe, no deps)."""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Mapping

from .settings import get_settings


# ----------------------------- JSON formatter -------------------------------


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        base: dict[str, Any] = {
            "ts": datetime.utcfromtimestamp(record.created).isoformat(
                timespec="milliseconds"
            )
            + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            base["exc"] = self.formatException(record.exc_info)
        extra = getattr(record, "extra", None)
        if isinstance(extra, Mapping):
            base["extra"] = dict(extra)
        return json.dumps(base, ensure_ascii=False)


# ---------------------------- Console formatter -----------------------------


class _ConsoleFormatter(logging.Formatter):
    _DIM = "\x1b[90m"
    _RESET = "\x1b[0m"
    _LEVEL = {
        "DEBUG": "\x1b[36m",
        "INFO": "\x1b[32m",
        "WARNING": "\x1b[33m",
        "ERROR": "\x1b[31m",
        "CRITICAL": "\x1b[35m",
    }

    def __init__(self, use_color: bool) -> None:
        super().__init__(datefmt="%H:%M:%S")
        self.use_color = bool(use_color and sys.stderr.isatty())

    def format(self, r: logging.LogRecord) -> str:  # noqa: D401
        ts = datetime.fromtimestamp(r.created).strftime("%H:%M:%S")
        level, name, msg = r.levelname, r.name, r.getMessage()
        suffix = "\n" + self.formatException(r.exc_info) if r.exc_info else ""
        if not self.use_color:
            return f"{ts} {level:8} {name}: {msg}{suffix}"
        lc = self._LEVEL.get(level, "")
        dim = self._DIM
        rst = self._RESET
        return f"{dim}{ts}{rst} {lc}{level:8}{rst} {dim}{name}{rst}: {msg}{suffix}"


# ------------------------------- Configurator --------------------------------

_configured = False


def _safe_file_handler(path: str, level: int) -> logging.Handler | None:
    """Try to create a JSON file handler; fall back to console on failure."""
    try:
        d = os.path.dirname(path)
        if d and not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        fh = logging.FileHandler(path, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(_JsonFormatter())
        return fh
    except OSError as e:
        sys.stderr.write(
            f"[logging] WARN cannot write to '{path}' ({e.__class__.__name__}: {e}). "
            "Falling back to console.\n"
        )
        return None


def configure_logging(*, force: bool = False) -> None:
    """Configure root logger once from settings; safe fallbacks for file sink."""
    global _configured  # noqa: PLW0603
    if _configured and not force:
        return

    st = get_settings()
    level = getattr(logging, str(st.log.level).upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)
    for h in list(root.handlers):
        root.removeHandler(h)

    handler: logging.Handler | None = None
    if st.log.json_file:
        handler = _safe_file_handler(st.log.json_file, level)

    if handler is None:
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(level)
        handler.setFormatter(_ConsoleFormatter(use_color=bool(st.log.color)))

    root.addHandler(handler)

    # Align noisy libs
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy"):
        logging.getLogger(name).setLevel(level)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    if not _configured:
        configure_logging()
    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger"]
