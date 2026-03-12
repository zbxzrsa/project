from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import CurrentUser, get_current_active_user
from backend.models import ReviewFeedback
from pydantic import BaseModel


router = APIRouter(prefix="/feedback", tags=["Review Feedback"])


class ReviewFeedbackCreate(BaseModel):
    review_id: str
    issue_id: Optional[str] = None
    action: str
    comment: Optional[str] = None


class ReviewFeedbackResponse(BaseModel):
    id: str
    review_id: str
    issue_id: Optional[str]
    user_id: str
    action: str
    comment: Optional[str]
    created_at: str


@router.post("", response_model=ReviewFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: ReviewFeedbackCreate,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """SRS-011: Capture user feedback (Accept/Dismiss) on review comments"""
    
    if feedback.action not in ["accepted", "dismissed", "fixed"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be one of: accepted, dismissed, fixed"
        )
    
    new_feedback = ReviewFeedback(
        id=feedback.review_id + "_" + str(hash(feedback.issue_id or ""))[:8],
        review_id=feedback.review_id,
        issue_id=feedback.issue_id,
        user_id=user.id,
        action=feedback.action,
        comment=feedback.comment,
    )
    
    db.add(new_feedback)
    await db.commit()
    await db.refresh(new_feedback)
    
    return ReviewFeedbackResponse(
        id=new_feedback.id,
        review_id=new_feedback.review_id,
        issue_id=new_feedback.issue_id,
        user_id=new_feedback.user_id,
        action=new_feedback.action,
        comment=new_feedback.comment,
        created_at=new_feedback.created_at.isoformat(),
    )


@router.get("/review/{review_id}", response_model=List[ReviewFeedbackResponse])
async def get_feedback_for_review(
    review_id: str,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all feedback for a review"""
    
    result = await db.execute(
        select(ReviewFeedback)
        .where(ReviewFeedback.review_id == review_id)
        .order_by(ReviewFeedback.created_at.desc())
    )
    feedbacks = result.scalars().all()
    
    return [
        ReviewFeedbackResponse(
            id=f.id,
            review_id=f.review_id,
            issue_id=f.issue_id,
            user_id=f.user_id,
            action=f.action,
            comment=f.comment,
            created_at=f.created_at.isoformat(),
        )
        for f in feedbacks
    ]


@router.get("/issue/{issue_id}", response_model=List[ReviewFeedbackResponse])
async def get_feedback_for_issue(
    issue_id: str,
    user: CurrentUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all feedback for a specific issue"""
    
    result = await db.execute(
        select(ReviewFeedback)
        .where(ReviewFeedback.issue_id == issue_id)
        .order_by(ReviewFeedback.created_at.desc())
    )
    feedbacks = result.scalars().all()
    
    return [
        ReviewFeedbackResponse(
            id=f.id,
            review_id=f.review_id,
            issue_id=f.issue_id,
            user_id=f.user_id,
            action=f.action,
            comment=f.comment,
            created_at=f.created_at.isoformat(),
        )
        for f in feedbacks
    ]
