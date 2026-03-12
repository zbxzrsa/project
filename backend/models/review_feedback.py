import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from backend.core.database import Base


class ReviewFeedback(Base):
    __tablename__ = "review_feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String(36), ForeignKey("reviews.id"), nullable=False, index=True)
    issue_id = Column(String(255), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    comment = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
