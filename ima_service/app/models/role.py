import uuid
from sqlalchemy import Column, String, Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base_class import Base, TimestampMixin
from app.schemas.role import RoleName


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(
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
