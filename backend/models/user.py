import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import JSON

from backend.core.database import Base
from backend.core.permissions import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default=UserRole.USER.value)
    is_active = Column(String(10), default="true")
    is_superuser = Column(String(10), default="false")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # OAuth fields
    github_id = Column(String(100), unique=True, nullable=True)
    github_access_token = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)

    tenant = relationship("Tenant", back_populates="users", foreign_keys=[tenant_id])
    audit_logs = relationship("AuditLog", back_populates="user", foreign_keys="[AuditLog.user_id]")
