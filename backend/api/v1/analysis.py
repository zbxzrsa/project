from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, status, BackgroundTasks
from pydantic import BaseModel

from backend.core.dependencies import CurrentUser, require_permission
from backend.core.permissions import Permission
from backend.services.graph_builder import GraphBuilder
from backend.core.logging import logger


router = APIRouter(prefix="/analysis", tags=["Analysis"])


class AnalysisRequest(BaseModel):
    project_id: str
    code_directory: str


class AnalysisResponse(BaseModel):
    status: str
    entities_created: int
    relations_created: int
    message: str


class DependencyGraphResponse(BaseModel):
    data: List[dict]


class CircularDependencyResponse(BaseModel):
    cycles: List[dict]


async def run_analysis_background(project_id: str, code_directory: str):
    try:
        builder = GraphBuilder(project_id)
        await builder.analyze_codebase(code_directory)
        await builder.build_graph()
        logger.info(f"Background analysis completed for project {project_id}")
    except Exception as e:
        logger.error(f"Background analysis failed: {e}")


@router.post("/architecture", response_model=AnalysisResponse)
async def analyze_architecture(
    analysis_request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(require_permission(Permission.RUN_ANALYSIS)),
):
    background_tasks.add_task(
        run_analysis_background,
        analysis_request.project_id,
        analysis_request.code_directory,
    )

    return AnalysisResponse(
        status="started",
        entities_created=0,
        relations_created=0,
        message="Analysis started in background",
    )


@router.get("/dependencies/{project_id}", response_model=DependencyGraphResponse)
async def get_dependency_graph(
    project_id: str,
    entity_id: Optional[str] = None,
    depth: int = 3,
    user: CurrentUser = Depends(require_permission(Permission.READ_ANALYSIS)),
):
    builder = GraphBuilder(project_id)
    data = await builder.get_dependency_graph(entity_id, depth)
    return DependencyGraphResponse(data=data.get("data", []))


@router.get("/circular-dependencies/{project_id}", response_model=CircularDependencyResponse)
async def find_circular_dependencies(
    project_id: str,
    user: CurrentUser = Depends(require_permission(Permission.READ_ANALYSIS)),
):
    builder = GraphBuilder(project_id)
    cycles = await builder.find_circular_dependencies()
    return CircularDependencyResponse(cycles=cycles)


@router.delete("/graph/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_graph(
    project_id: str,
    user: CurrentUser = Depends(require_permission(Permission.RUN_ANALYSIS)),
):
    builder = GraphBuilder(project_id)
    await builder.clear_graph()
