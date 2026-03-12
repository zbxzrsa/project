from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class ReviewStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ReviewBase(BaseModel):
    pass


class ReviewCreate(BaseModel):
    project_id: UUID
    commit_sha: Optional[str] = Field(None, max_length=40)
    branch: Optional[str] = Field(None, max_length=255)
    pr_number: Optional[int] = None


class ReviewUpdate(BaseModel):
    status: Optional[ReviewStatus] = None
    results: Optional[dict] = None
    error_message: Optional[str] = None


class ReviewResponse(ReviewBase):
    id: UUID
    project_id: UUID
    commit_sha: Optional[str]
    branch: Optional[str]
    pr_number: Optional[int]
    status: str
    results: dict
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
