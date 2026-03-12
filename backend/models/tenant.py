import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy import JSON

from backend.core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan", foreign_keys="[User.tenant_id]")
    projects = relationship("Project", back_populates="tenant", cascade="all, delete-orphan", foreign_keys="[Project.tenant_id]")
    feature_flags = relationship("FeatureFlag", back_populates="tenant", cascade="all, delete-orphan", foreign_keys="[FeatureFlag.tenant_id]")
    audit_logs = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan", foreign_keys="[AuditLog.tenant_id]")
