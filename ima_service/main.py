# FILE: ima_service/main.py
"""
ASGI shim so `uvicorn ima_service.main:app` works.

This re-exports the FastAPI `app` defined in `ima_service.app.main`.
"""

from __future__ import annotations

# Re-export: keep the import path stable for Taskfile/uvicorn
from ima_service.app.main import app as app  # noqa: F401

__all__ = ["app"]
