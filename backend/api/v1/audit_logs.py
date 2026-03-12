from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, require_permission
from backend.core.permissions import Permission
from backend.schemas.audit_log import AuditLogResponse
from backend.services.audit import service as audit_service


router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    user_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    user: CurrentUser = Depends(require_permission(Permission.READ_AUDIT_LOGS)),
    db: AsyncSession = Depends(get_db),
):
    """Get audit logs (admin only)."""
    return await audit_service.get_audit_logs(
        db=db,
        tenant_id=user.tenant_id,
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        skip=skip,
        limit=limit,
    )
