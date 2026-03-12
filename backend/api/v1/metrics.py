from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, get_current_active_user
from backend.services.metrics.service import MetricsCalculator, ReportExporter


router = APIRouter(prefix="/metrics", tags=["Metrics & Reports"])


@router.get("")
async def get_metrics(
    days: int = Query(30, ge=1, le=365),
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get code quality metrics for dashboard"""
    
    calculator = MetricsCalculator(db, str(user.tenant_id))
    metrics = await calculator.calculate_metrics(days)
    
    return metrics


@router.get("/export")
async def export_metrics(
    format: str = Query("json", regex="^(json|csv|markdown)$"),
    days: int = Query(30, ge=1, le=365),
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """URS-06: Export code quality metrics dashboard with exportable reports"""
    
    calculator = MetricsCalculator(db, str(user.tenant_id))
    metrics = await calculator.calculate_metrics(days)
    
    exporter = ReportExporter()
    
    if format == "csv":
        content = exporter.export_csv(metrics)
        media_type = "text/csv"
        filename = f"code_quality_metrics_{days}days.csv"
        
    elif format == "markdown":
        content = exporter.export_markdown(metrics)
        media_type = "text/markdown"
        filename = f"code_quality_metrics_{days}days.md"
        
    else:
        content = exporter.export_json(metrics)
        media_type = "application/json"
        filename = f"code_quality_metrics_{days}days.json"
    
    return StreamingResponse(
        content=[content],
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/technical-debt")
async def get_technical_debt(
    days: int = Query(30, ge=1, le=365),
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get technical debt analysis"""
    
    calculator = MetricsCalculator(db, str(user.tenant_id))
    metrics = await calculator.calculate_metrics(days)
    
    td = metrics.get("technical_debt", {})
    
    return {
        "total_issues": td.get("total_issues", 0),
        "by_severity": td.get("by_severity", {}),
        "estimated_hours": td.get("estimated_hours", 0),
        "by_category": metrics.get("issues_by_category", {}),
    }


@router.get("/trends")
async def get_quality_trends(
    days: int = Query(30, ge=7, le=365),
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get quality trends over time"""
    
    calculator = MetricsCalculator(db, str(user.tenant_id))
    metrics = await calculator.calculate_metrics(days)
    
    return {
        "trend": metrics.get("quality_trend", []),
        "period_days": days,
    }
