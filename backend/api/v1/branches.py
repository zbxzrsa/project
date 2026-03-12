from typing import List, Optional
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, get_current_active_user
from backend.core.permissions import Permission, require_permission
from backend.models import Branch, Project, AnalysisTask
from backend.schemas import Tenant
from pydantic import BaseModel


router = APIRouter(prefix="/branches", tags=["Branches"])


class BranchResponse(BaseModel):
    id: str
    project_id: str
    name: str
    is_default: bool
    last_commit_sha: Optional[str]
    last_analysis_at: Optional[str]
    analysis_status: str
    issues_count: int
    critical_issues: int
    score: Optional[int]
    created_at: str


class BranchSyncRequest(BaseModel):
    project_id: str


@router.get("/project/{project_id}", response_model=List[BranchResponse])
async def list_branches(
    project_id: str,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List all branches for a project"""
    
    result = await db.execute(
        select(Branch).where(Branch.project_id == project_id)
    )
    branches = result.scalars().all()
    
    return [
        BranchResponse(
            id=b.id,
            project_id=b.project_id,
            name=b.name,
            is_default=b.is_default,
            last_commit_sha=b.last_commit_sha,
            last_analysis_at=b.last_analysis_at.isoformat() if b.last_analysis_at else None,
            analysis_status=b.analysis_status,
            issues_count=b.issues_count,
            critical_issues=b.critical_issues,
            score=b.score,
            created_at=b.created_at.isoformat(),
        )
        for b in branches
    ]


@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(
    branch_id: str,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get branch details"""
    
    result = await db.execute(
        select(Branch).where(Branch.id == branch_id)
    )
    branch = result.scalar_one_or_none()
    
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    return BranchResponse(
        id=branch.id,
        project_id=branch.project_id,
        name=branch.name,
        is_default=branch.is_default,
        last_commit_sha=branch.last_commit_sha,
        last_analysis_at=branch.last_analysis_at.isoformat() if branch.last_analysis_at else None,
        analysis_status=branch.analysis_status,
        issues_count=branch.issues_count,
        critical_issues=branch.critical_issues,
        score=branch.score,
        created_at=branch.created_at.isoformat(),
    )


@router.post("/project/{project_id}/sync")
async def sync_branches(
    project_id: str,
    user: CurrentUser = Depends(require_permission(Permission.RUN_ANALYSIS)),
    db: AsyncSession = Depends(get_db),
):
    """Sync branches from GitHub repository"""
    
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if not project.repository_url:
        raise HTTPException(status_code=400, detail="Project has no repository URL")
    
    if not user.github_access_token:
        raise HTTPException(status_code=400, detail="No GitHub token linked")
    
    from backend.services.github_sync import RepositorySyncService
    
    try:
        parts = project.repository_url.replace("https://github.com/", "").split("/")
        owner, repo = parts[0], parts[1]
        
        sync_service = RepositorySyncService(user.github_access_token)
        sync_data = await sync_service.sync_repository(owner, repo)
        
        existing_branches = await db.execute(
            select(Branch).where(Branch.project_id == project_id)
        )
        existing = {b.name: b for b in existing_branches.scalars().all()}
        
        for branch_data in sync_data["branches"]:
            if branch_data["name"] in existing:
                branch = existing[branch_data["name"]]
                branch.last_commit_sha = branch_data["sha"]
                branch.last_commit_message = branch_data.get("last_commit_message")
                branch.last_commit_author = branch_data.get("last_commit_author")
            else:
                branch = Branch(
                    id=str(uuid4()),
                    project_id=project_id,
                    name=branch_data["name"],
                    is_default=branch_data.get("protected", False),
                    last_commit_sha=branch_data["sha"],
                    last_commit_message=branch_data.get("last_commit_message"),
                    last_commit_author=branch_data.get("last_commit_author"),
                )
                db.add(branch)
        
        await db.commit()
        
        return {"message": "Branches synced", "count": len(sync_data["branches"])}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")
