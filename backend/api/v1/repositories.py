import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel


router = APIRouter(prefix="/repositories", tags=["Repositories"])


class RepositoryValidateRequest(BaseModel):
    url: str


class RepositoryValidateResponse(BaseModel):
    valid: bool
    owner: Optional[str]
    repo: Optional[str]
    error: Optional[str]


GITHUB_URL_PATTERN = re.compile(r'^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?$/?$')


@router.post("/validate", response_model=RepositoryValidateResponse)
async def validate_repository(request: RepositoryValidateRequest):
    """SRS-005: Validate GitHub repository URL before adding"""
    
    url = request.url.strip()
    
    if not url:
        return RepositoryValidateResponse(
            valid=False,
            owner=None,
            repo=None,
            error="URL is required"
        )
    
    match = GITHUB_URL_PATTERN.match(url)
    
    if not match:
        return RepositoryValidateResponse(
            valid=False,
            owner=None,
            repo=None,
            error="Invalid GitHub URL format. Expected: https://github.com/{owner}/{repo}"
        )
    
    owner, repo = match.groups()
    
    return RepositoryValidateResponse(
        valid=True,
        owner=owner,
        repo=repo,
        error=None
    )
