from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class TenantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    settings: Optional[dict] = {}


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    settings: Optional[dict] = None


class TenantResponse(TenantBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
