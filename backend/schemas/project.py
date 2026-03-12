from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    repository_url: Optional[str] = Field(None, max_length=500)
    settings: Optional[dict] = {}


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    repository_url: Optional[str] = Field(None, max_length=500)
    settings: Optional[dict] = None


class ProjectResponse(ProjectBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
