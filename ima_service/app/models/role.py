"""SQLAlchemy Role model with Base and timestamp mixin."""

import uuid

from sqlalchemy import Boolean, Column
from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..db.base_class import Base, TimestampMixin
from ..schemas.role import RoleName


class Role(Base, TimestampMixin):  # pylint: disable=too-few-public-methods
    """SQLAlchemy model representing a user role in the IAM service."""

    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(  # type: ignore[var-annotated]
        SAEnum(RoleName, name="role_name_enum", native_enum=True),
        nullable=False,
        unique=True,
    )
    description = Column(String, nullable=True)
    is_system = Column(Boolean, default=False, nullable=False)

    users = relationship(
        "app.models.user.User",
        secondary="user_roles",
        back_populates="roles",
        lazy="selectin",
    )
