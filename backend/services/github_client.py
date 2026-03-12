import hmac
import hashlib
import json
from typing import Optional, Dict, Any, List
import httpx
from pydantic import BaseModel

from backend.core.config import settings
from backend.core.logging import logger


class GitHubPullRequest(BaseModel):
    id: int
    number: int
    title: str
    body: Optional[str] = None
    head_sha: str
    base_sha: str
    html_url: str


class GitHubWebhookEvent(BaseModel):
    action: str
    pull_request: Dict[str, Any]
    repository: Dict[str, Any]


class GitHubClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.github.com"

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=f"{self.base_url}{endpoint}",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
            return response.json() if response.text else {}

    async def get_pull_request(
        self, owner: str, repo: str, pull_number: int
    ) -> GitHubPullRequest:
        data = await self._request(
            "GET", f"/repos/{owner}/{repo}/pulls/{pull_number}"
        )
        return GitHubPullRequest(
            id=data["id"],
            number=data["number"],
            title=data["title"],
            body=data.get("body"),
            head_sha=data["head"]["sha"],
            base_sha=data["base"]["sha"],
            html_url=data["html_url"],
        )

    async def get_pull_request_files(
        self, owner: str, repo: str, pull_number: int
    ) -> List[Dict[str, Any]]:
        return await self._request(
            "GET", f"/repos/{owner}/{repo}/pulls/{pull_number}/files"
        )

    async def get_file_content(
        self, owner: str, repo: str, path: str, ref: str
    ) -> str:
        import base64

        data = await self._request(
            "GET", f"/repos/{owner}/{repo}/contents/{path}", {"ref": ref}
        )
        if data.get("encoding") == "base64" and data.get("content"):
            return base64.b64decode(data["content"]).decode("utf-8")
        return ""

    async def create_pull_request_review_comment(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        commit_id: str,
        path: str,
        line: int,
    ) -> Dict[str, Any]:
        return await self._request(
            "POST",
            f"/repos/{owner}/{repo}/pulls/{pull_number}/comments",
            {
                "body": body,
                "commit_id": commit_id,
                "path": path,
                "line": line,
                "side": "RIGHT",
            },
        )

    async def create_pull_request_review(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        event: str = "COMMENT",
    ) -> Dict[str, Any]:
        return await self._request(
            "POST",
            f"/repos/{owner}/{repo}/pulls/{pull_number}/reviews",
            {
                "body": body,
                "event": event,
            },
        )


def verify_github_signature(
    payload: bytes, signature: str, secret: str
) -> bool:
    if not signature:
        return False
    expected_signature = (
        "sha256=" + hmac.new(
            secret.encode(), payload, hashlib.sha256
        ).hexdigest()
    )
    return hmac.compare_digest(expected_signature, signature)


def format_review_as_markdown(
    summary: str,
    score: int,
    issues: List[Dict[str, Any]],
    strengths: List[str],
    improvements: List[str],
) -> str:
    lines = [
        f"## Code Review Results",
        "",
        f"**Overall Score:** {score}/100",
        "",
        f"### Summary",
        summary,
        "",
    ]

    if issues:
        lines.append("### Issues Found")
        severity_order = ["critical", "high", "medium", "low", "info"]
        sorted_issues = sorted(
            issues,
            key=lambda x: severity_order.index(x.get("severity", "info"))
            if x.get("severity") in severity_order
            else 999,
        )
        for issue in sorted_issues:
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
                "info": "🔵",
            }.get(issue.get("severity", "info"), "⚪")

            lines.append(
                f"- {severity_emoji} **[{issue.get('severity', 'info').upper()}]** "
                f"{issue.get('title', 'Issue')}"
            )
            if issue.get("location", {}).get("file"):
                lines.append(
                    f"  - File: {issue['location']['file']}"
                )
            if issue.get("suggestion"):
                lines.append(f"  - Suggestion: {issue['suggestion']}")
            lines.append("")

    if strengths:
        lines.append("### Strengths")
        for strength in strengths:
            lines.append(f"- ✅ {strength}")
        lines.append("")

    if improvements:
        lines.append("### Suggested Improvements")
        for improvement in improvements:
            lines.append(f"- 💡 {improvement}")
        lines.append("")

    return "\n".join(lines)
