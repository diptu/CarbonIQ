# app/db/base
"""
Base import hub for SQLAlchemy models.

This module ensures that all models are imported so that Alembic's
autogenerate feature can detect them.
"""

from ima_service.app.db.base_class import Base  # pylint: disable=unused-import
from ima_service.app.models.user import User  # pylint: disable=unused-import
