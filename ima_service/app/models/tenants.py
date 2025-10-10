# app/models/tenants.py
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base_class import Base
import uuid


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    domain = Column(String(255), nullable=False, unique=True)
    schema_name = Column(String(100), nullable=False, unique=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    parent = relationship("Tenant", remote_side=[id], backref="sub_tenants")
    users = relationship("User", back_populates="tenant")
