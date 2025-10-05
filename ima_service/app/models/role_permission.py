from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..db.base_class import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), primary_key=True)
    permission_id = Column(
        UUID(as_uuid=True), ForeignKey("permissions.id"), primary_key=True
    )

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
