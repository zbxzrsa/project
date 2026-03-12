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

    avg_score = 0
    critical_issues = 0

    recent_reviews_result = await db.execute(
        select(Review, Project.name)
        .join(Project, Review.project_id == Project.id)
        .where(Project.tenant_id == user.tenant_id)
        .order_by(Review.created_at.desc())
        .limit(10)
    )

    scores = []
    recent_reviews = []
    for review, name in recent_reviews_result.all():
        review_score = 0
        if review.results and isinstance(review.results, dict):
            review_score = review.results.get("score", 0)
            if isinstance(review_score, int):
                scores.append(review_score)
            issues = review.results.get("issues", [])
            if isinstance(issues, list):
                critical_issues += sum(1 for i in issues if i.get("severity") in ["critical", "high"])
        
        recent_reviews.append({
            "id": str(review.id),
            "projectName": name,
            "score": review_score,
            "status": review.status,
            "createdAt": review.created_at.isoformat() if review.created_at else "",
        })

    if scores:
        avg_score = sum(scores) // len(scores)

    return {
        "stats": {
            "totalProjects": total_projects,
            "totalReviews": total_reviews,
            "avgScore": avg_score,
            "criticalIssues": critical_issues,
        },
        "recent_reviews": recent_reviews,
    }
