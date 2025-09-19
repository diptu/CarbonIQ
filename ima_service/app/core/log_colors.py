# FILE: ima_service/app/core/log_colors.py
"""ANSI color helpers for lightweight, human-friendly log accents."""

from __future__ import annotations

# Keep tiny and reusable; use only when you really need shell color accents.
CLR_OK = "\x1b[32m"
CLR_WARN = "\x1b[33m"
CLR_ERR = "\x1b[31m"
CLR_RESET = "\x1b[0m"
