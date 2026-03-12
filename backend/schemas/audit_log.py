from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AuditLogBase(BaseModel):
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    details: Optional[dict] = {}


class AuditLogResponse(AuditLogBase):
    id: UUID
    tenant_id: UUID
    user_id: Optional[UUID]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
