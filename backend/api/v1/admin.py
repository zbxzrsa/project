from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.core.dependencies import CurrentUser, require_permission
from backend.core.permissions import Permission
from backend.core.database import get_db
from backend.models import User, Project, Review


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_admin_stats(
    user: CurrentUser = Depends(require_permission(Permission.SYSTEM_SETTINGS)),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar() or 0

    projects_result = await db.execute(select(func.count(Project.id)))
    total_projects = projects_result.scalar() or 0

    reviews_result = await db.execute(select(func.count(Review.id)))
    total_reviews = reviews_result.scalar() or 0

    active_users_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == "true")
    )
    active_users = active_users_result.scalar() or 0

    return {
        "totalUsers": total_users,
        "totalProjects": total_projects,
        "totalReviews": total_reviews,
        "activeUsers": active_users,
    }
