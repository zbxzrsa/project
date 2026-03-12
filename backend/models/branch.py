import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Integer, Text
from sqlalchemy.orm import relationship
from backend.core.database import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    is_default = Column(Boolean, default=False)
    last_commit_sha = Column(String(40), nullable=True)
    last_commit_message = Column(Text, nullable=True)
    last_commit_author = Column(String(255), nullable=True)
    last_analysis_at = Column(DateTime, nullable=True)
    analysis_status = Column(String(50), default="pending")
    issues_count = Column(Integer, default=0)
    critical_issues = Column(Integer, default=0)
    score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="branches")
    analyses = relationship("AnalysisTask", back_populates="branch")
