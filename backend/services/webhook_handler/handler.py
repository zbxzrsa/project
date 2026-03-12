import hmac
import hashlib
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel


class FileChange(BaseModel):
    path: str
    status: str
    additions: int
    deletions: int
    content: Optional[str] = None
    diff: Optional[str] = None


class ReviewRequest(BaseModel):
    project_id: str
    commit_sha: Optional[str] = None
    branch: Optional[str] = None
    pr_number: Optional[int] = None
    event_type: str
    files: List[FileChange]
    author: Optional[str] = None
    timestamp: datetime


class WebhookEventType:
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    PULL_REQUEST_REVIEW = "pull_request_review"


def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature:
        return False
    
    computed_signature = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_signature, signature)


def parse_push_event(payload: dict) -> Dict[str, Any]:
    """Parse GitHub push event."""
    commits = payload.get("commits", [])
    files = []
    
    for commit in commits:
        for file_data in commit.get("added", []):
            files.append(FileChange(
                path=file_data,
                status="added",
                additions=0,
                deletions=0,
            ))
        for file_data in commit.get("removed", []):
            files.append(FileChange(
                path=file_data,
                status="deleted",
                additions=0,
                deletions=0,
            ))
        for file_data in commit.get("modified", []):
            files.append(FileChange(
                path=file_data,
                status="modified",
                additions=0,
                deletions=0,
            ))
    
    return {
        "commit_sha": payload.get("after"),
        "branch": payload.get("ref", "").replace("refs/heads/", ""),
        "files": files,
        "author": commits[0].get("author", {}).get("name") if commits else None,
    }


def parse_pull_request_event(payload: dict) -> Dict[str, Any]:
    """Parse GitHub pull request event."""
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    
    files = []
    if action in ["opened", "synchronize", "reopened"]:
        changed_files = pr.get("changed_files", 0)
        for _ in range(changed_files):
            files.append(FileChange(
                path="",
                status="modified",
                additions=0,
                deletions=0,
            ))
    
    return {
        "pr_number": pr.get("number"),
        "commit_sha": pr.get("head", {}).get("sha"),
        "branch": pr.get("head", {}).get("ref"),
        "files": files,
        "author": pr.get("user", {}).get("login"),
        "action": action,
    }


def create_review_request(
    project_id: str,
    event_type: str,
    payload: dict,
) -> ReviewRequest:
    """Create a ReviewRequest from webhook payload."""
    files = []
    
    if event_type == WebhookEventType.PUSH:
        parsed = parse_push_event(payload)
        files = parsed["files"]
    elif event_type == WebhookEventType.PULL_REQUEST:
        parsed = parse_pull_request_event(payload)
        files = parsed["files"]
    
    return ReviewRequest(
        project_id=project_id,
        event_type=event_type,
        files=files,
    )
