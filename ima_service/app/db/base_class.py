# app/db/base_class
"""Base class for SQLAlchemy models."""

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """Custom declarative base class for all SQLAlchemy models."""

    @declared_attr  # type: ignore[arg-type]
    def __tablename__(cls) -> str:  # pylint: disable=no-self-argument
        """Generate __tablename__ automatically from class name."""
        return cls.__name__.lower()
