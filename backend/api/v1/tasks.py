from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, get_current_active_user
from backend.models import AnalysisTask
from pydantic import BaseModel


router = APIRouter(prefix="/tasks", tags=["Analysis Tasks"])


class TaskResponse(BaseModel):
    id: str
    project_id: str
    branch_id: str | None
    branch_name: str
    commit_sha: str | None
    status: str
    stage: str
    progress: int
    error_message: str | None
    created_at: str
    started_at: str | None
    completed_at: str | None


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    project_id: str | None = None,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all analysis tasks"""
    
    query = select(AnalysisTask).order_by(desc(AnalysisTask.created_at))
    
    if project_id:
        query = query.where(AnalysisTask.project_id == project_id)
    
    result = await db.execute(query.limit(100))
    tasks = result.scalars().all()
    
    return [
        TaskResponse(
            id=t.id,
            project_id=t.project_id,
            branch_id=t.branch_id,
            branch_name=t.branch_name,
            commit_sha=t.commit_sha,
            status=t.status,
            stage=t.stage,
            progress=t.progress,
            error_message=t.error_message,
            created_at=t.created_at.isoformat() if t.created_at else "",
            started_at=t.started_at.isoformat() if t.started_at else None,
            completed_at=t.completed_at.isoformat() if t.completed_at else None,
        )
        for t in tasks
    ]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get task details"""
    
    result = await db.execute(
        select(AnalysisTask).where(AnalysisTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        branch_id=task.branch_id,
        branch_name=task.branch_name,
        commit_sha=task.commit_sha,
        status=task.status,
        stage=task.stage,
        progress=task.progress,
        error_message=task.error_message,
        created_at=task.created_at.isoformat() if task.created_at else "",
        started_at=task.started_at.isoformat() if task.started_at else None,
        completed_at=task.completed_at.isoformat() if task.completed_at else None,
    )


@router.post("/{task_id}/retry")
async def retry_task(
    task_id: str,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Retry a failed task"""
    
    result = await db.execute(
        select(AnalysisTask).where(AnalysisTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = "pending"
    task.error_message = None
    await db.commit()
    
    return {"message": "Task queued for retry"}


@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel a pending/queued task"""
    
    result = await db.execute(
        select(AnalysisTask).where(AnalysisTask.id == task_id)
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status not in ["pending", "queued"]:
        raise HTTPException(status_code=400, detail="Only pending/queued tasks can be cancelled")
    
    task.status = "cancelled"
    await db.commit()
    
    return {"message": "Task cancelled"}
