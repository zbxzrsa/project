from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class FeatureFlagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    enabled: bool = False
    rules: Optional[dict] = {}


class FeatureFlagCreate(FeatureFlagBase):
    pass


class FeatureFlagUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    enabled: Optional[bool] = None
    rules: Optional[dict] = None


class FeatureFlagResponse(FeatureFlagBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
