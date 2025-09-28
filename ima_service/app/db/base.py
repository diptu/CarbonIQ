# app/db/base.py
from .base_class import Base

# Import models only once to register them
import app.models.user  # noqa: F401
import app.models.role  # noqa: F401
import app.models.user_roles  # noqa: F401

__all__ = ["Base"]
