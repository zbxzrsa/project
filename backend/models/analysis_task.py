import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from backend.core.database import Base


class AnalysisTask(Base):
    __tablename__ = "analysis_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False, index=True)
    branch_id = Column(String(36), ForeignKey("branches.id"), nullable=True, index=True)
    branch_name = Column(String(255), nullable=False)
    commit_sha = Column(String(40), nullable=True)
    status = Column(String(50), default="pending")
    stage = Column(String(100), default="queued")
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project")
    branch = relationship("Branch", back_populates="analyses")
