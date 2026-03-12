from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, require_permission
from backend.core.permissions import Permission
from backend.core.exceptions import NotFoundException
from backend.models import Project
from backend.schemas import ProjectCreate, ProjectUpdate, ProjectResponse


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    user: CurrentUser = Depends(require_permission(Permission.READ_PROJECT)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project)
        .where(Project.tenant_id == user.tenant_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    user: CurrentUser = Depends(require_permission(Permission.READ_PROJECT)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == user.tenant_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException("Project", str(project_id))
    return project


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    user: CurrentUser = Depends(require_permission(Permission.CREATE_PROJECT)),
    db: AsyncSession = Depends(get_db),
):
    project = Project(
        tenant_id=user.tenant_id,
        **project_data.model_dump(),
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    user: CurrentUser = Depends(require_permission(Permission.UPDATE_PROJECT)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == user.tenant_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException("Project", str(project_id))

    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    user: CurrentUser = Depends(require_permission(Permission.DELETE_PROJECT)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.tenant_id == user.tenant_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundException("Project", str(project_id))

    await db.delete(project)
    await db.commit()
