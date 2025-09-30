"""SQLAlchemy User model with Base and timestamp mixin."""

import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..db.base_class import Base, TimestampMixin


class User(Base, TimestampMixin):  # pylint: disable=too-few-public-methods
    """SQLAlchemy model representing a user in the IAM service."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    roles = relationship(
        "app.models.role.Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )
