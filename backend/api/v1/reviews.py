from uuid import UUID
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, require_permission
from backend.core.permissions import Permission
from backend.core.exceptions import NotFoundException
from backend.models import Review, ReviewStatus
from backend.schemas import ReviewCreate, ReviewUpdate, ReviewResponse
from backend.services.code_review import code_review_service


router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("", response_model=List[ReviewResponse])
async def list_reviews(
    project_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    user: CurrentUser = Depends(require_permission(Permission.READ_REVIEW)),
    db: AsyncSession = Depends(get_db),
):
    query = select(Review).where(Review.project_id == str(project_id)) if project_id else select(Review)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: UUID,
    user: CurrentUser = Depends(require_permission(Permission.READ_REVIEW)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Review).where(Review.id == str(review_id))
    )
    review = result.scalar_one_or_none()
    if not review:
        raise NotFoundException("Review", str(review_id))
    return review


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    user: CurrentUser = Depends(require_permission(Permission.CREATE_REVIEW)),
    db: AsyncSession = Depends(get_db),
):
    review = Review(
        id=str(UUID),
        project_id=str(review_data.project_id),
        commit_sha=review_data.commit_sha,
        branch=review_data.branch,
        pr_number=review_data.pr_number,
        status=ReviewStatus.PENDING,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    
    return review


@router.post("/{review_id}/analyze")
async def analyze_review(
    review_id: UUID,
    code: str,
    language: str = "python",
    user: CurrentUser = Depends(require_permission(Permission.RUN_ANALYSIS)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Review).where(Review.id == str(review_id))
    )
    review = result.scalar_one_or_none()
    if not review:
        raise NotFoundException("Review", str(review_id))
    
    await db.execute(
        update(Review)
        .where(Review.id == str(review_id))
        .values(status=ReviewStatus.PROCESSING, started_at=datetime.utcnow())
    )
    await db.commit()
    
    try:
        review_result = await code_review_service.review_code(
            code=code,
            language=language,
            context={"review_id": str(review_id)}
        )
        
        await db.execute(
            update(Review)
            .where(Review.id == str(review_id))
            .values(
                status=ReviewStatus.COMPLETED,
                results={
                    "summary": review_result.summary,
                    "score": review_result.score,
                    "issues": [issue.model_dump() for issue in review_result.issues],
                    "strengths": review_result.strengths,
                    "improvements": review_result.improvements,
                },
                completed_at=datetime.utcnow()
            )
        )
        await db.commit()
        
        return {"status": "completed", "results": review_result.model_dump()}
        
    except Exception as e:
        await db.execute(
            update(Review)
            .where(Review.id == str(review_id))
            .values(
                status=ReviewStatus.FAILED,
                error_message=str(e),
                completed_at=datetime.utcnow()
            )
        )
        await db.commit()
        raise


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    user: CurrentUser = Depends(require_permission(Permission.UPDATE_PROJECT)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Review).where(Review.id == str(review_id))
    )
    review = result.scalar_one_or_none()
    if not review:
        raise NotFoundException("Review", str(review_id))

    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    await db.commit()
    await db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: UUID,
    user: CurrentUser = Depends(require_permission(Permission.DELETE_REVIEW)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Review).where(Review.id == str(review_id))
    )
    review = result.scalar_one_or_none()
    if not review:
        raise NotFoundException("Review", str(review_id))

    await db.delete(review)
    await db.commit()
