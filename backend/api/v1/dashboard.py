from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, get_current_active_user
from backend.models import Project, Review


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
async def get_dashboard(
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    projects_result = await db.execute(
        select(func.count(Project.id)).where(Project.tenant_id == user.tenant_id)
    )
    total_projects = projects_result.scalar() or 0

    reviews_result = await db.execute(
        select(func.count(Review.id))
        .join(Project, Review.project_id == Project.id)
        .where(Project.tenant_id == user.tenant_id)
    )
    total_reviews = reviews_result.scalar() or 0

    avg_score_result = await db.execute(
        select(func.avg(Review.score))
        .join(Project, Review.project_id == Project.id)
        .where(Project.tenant_id == user.tenant_id, Review.score.isnot(None))
    )
    avg_score = avg_score_result.scalar() or 0

    critical_result = await db.execute(
        select(func.count(Review.id))
        .join(Project, Review.project_id == Project.id)
        .where(
            Project.tenant_id == user.tenant_id,
            Review.results.contains("critical"),
        )
    )
    critical_issues = critical_result.scalar() or 0

    recent_reviews_result = await db.execute(
        select(Review, Project.name)
        .join(Project, Review.project_id == Project.id)
        .where(Project.tenant_id == user.tenant_id)
        .order_by(Review.created_at.desc())
        .limit(10)
    )
    recent_reviews = [
        {
            "id": str(review.id),
            "projectName": name,
            "score": review.score or 0,
            "status": review.status,
            "createdAt": review.created_at.isoformat() if review.created_at else "",
        }
        for review, name in recent_reviews_result.all()
    ]

    return {
        "stats": {
            "totalProjects": total_projects,
            "totalReviews": total_reviews,
            "avgScore": int(avg_score),
            "criticalIssues": critical_issues,
        },
        "recent_reviews": recent_reviews,
    }
