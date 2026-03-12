from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.dependencies import CurrentUser, require_permission
from backend.core.permissions import Permission
from backend.core.logging import logger


router = APIRouter(prefix="/settings", tags=["Settings"])


class AnalysisSettings(BaseModel):
    auto_review_on_pr: bool = True
    max_files_per_review: int = 10
    max_file_size_kb: int = 500
    severity_threshold: str = "medium"
    include_security_checks: bool = True
    include_style_checks: bool = True
    include_performance_checks: bool = True


class ComplianceSettings(BaseModel):
    enabled_standards: list[str] = ["iso_25010", "google_style"]
    auto_check_on_review: bool = True


class NotificationSettings(BaseModel):
    email_on_critical_issues: bool = True
    email_on_completion: bool = False
    webhook_url: Optional[str] = None


class SystemSettings(BaseModel):
    analysis: AnalysisSettings
    compliance: ComplianceSettings
    notifications: NotificationSettings


DEFAULT_SETTINGS = SystemSettings(
    analysis=AnalysisSettings(),
    compliance=ComplianceSettings(),
    notifications=NotificationSettings(),
)


@router.get("", response_model=SystemSettings)
async def get_settings(
    user: CurrentUser = Depends(require_permission(Permission.SYSTEM_SETTINGS)),
):
    """URS-07: Get system settings"""
    return DEFAULT_SETTINGS


@router.put("", response_model=SystemSettings)
async def update_settings(
    settings: SystemSettings,
    user: CurrentUser = Depends(require_permission(Permission.SYSTEM_SETTINGS)),
):
    """URS-07: Update system settings - Settings are saved immediately"""
    global DEFAULT_SETTINGS
    DEFAULT_SETTINGS = settings
    
    logger.info(f"User {user.id} updated system settings")
    
    return DEFAULT_SETTINGS


@router.post("/compliance/standards")
async def add_compliance_standard(
    standard: str,
    user: CurrentUser = Depends(require_permission(Permission.MANAGE_COMPLIANCE)),
):
    """Add a compliance standard"""
    if standard not in ["iso_25010", "iso_23396", "google_style"]:
        raise HTTPException(status_code=400, detail="Invalid standard")
    
    if standard not in DEFAULT_SETTINGS.compliance.enabled_standards:
        DEFAULT_SETTINGS.compliance.enabled_standards.append(standard)
        logger.info(f"User {user.id} added compliance standard: {standard}")
    
    return {"standards": DEFAULT_SETTINGS.compliance.enabled_standards}


@router.delete("/compliance/standards/{standard}")
async def remove_compliance_standard(
    standard: str,
    user: CurrentUser = Depends(require_permission(Permission.MANAGE_COMPLIANCE)),
):
    """Remove a compliance standard"""
    if standard in DEFAULT_SETTINGS.compliance.enabled_standards:
        DEFAULT_SETTINGS.compliance.enabled_standards.remove(standard)
        logger.info(f"User {user.id} removed compliance standard: {standard}")
    
    return {"standards": DEFAULT_SETTINGS.compliance.enabled_standards}


@router.get("/compliance/standards")
async def list_compliance_standards():
    """List available compliance standards"""
    return {
        "available": ["iso_25010", "iso_23396", "google_style"],
        "enabled": DEFAULT_SETTINGS.compliance.enabled_standards,
    }
