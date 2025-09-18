# FILE: ima_service/app/db/__init__.py
"""
DB package public surface.

Export only the declarative `Base`. Import session helpers directly from
`ima_service.app.db.session` where needed (e.g., get_db).
"""

from __future__ import annotations

from .base import Base

__all__ = ["Base"]
