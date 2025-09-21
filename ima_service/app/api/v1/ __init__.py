# ima_service/app/api/v1/__init__.py
"""API v1 package: aggregated router and submodules."""
# pylint: skip-file

from __future__ import annotations

from app.api.v1.routes import router

__all__ = ["router"]
