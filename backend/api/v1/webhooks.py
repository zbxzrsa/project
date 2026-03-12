from typing import Dict, Any
from fastapi import APIRouter, Request, Header, status
from pydantic import BaseModel

from backend.services.github_client import (
    GitHubClient,
    verify_github_signature,
    format_review_as_markdown,
)
from backend.tasks.code_review_tasks import review_code_task
from backend.core.config import settings
from backend.core.logging import logger


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


class WebhookResponse(BaseModel):
    message: str
    status: str


@router.post("/github", response_model=WebhookResponse)
async def github_webhook(
    request: Request,
    x_github_signature: str = Header(None),
    x_github_event: str = Header(None),
):
    payload = await request.body()

    if not verify_github_signature(
        payload,
        x_github_signature or "",
        settings.GITHUB_CLIENT_SECRET or "",
    ):
        logger.warning("Invalid GitHub webhook signature")
        return WebhookResponse(
            message="Invalid signature",
            status="rejected",
        )

    try:
        event_data = await request.json()
    except Exception:
        return WebhookResponse(
            message="Invalid payload",
            status="rejected",
        )

    if x_github_event == "pull_request":
        action = event_data.get("action")
        if action not in ["opened", "synchronize", "ready_for_review"]:
            return WebhookResponse(
                message=f"Ignored action: {action}",
                status="ignored",
            )

        pr = event_data.get("pull_request", {})
        repo = event_data.get("repository", {})
        repo_full_name = repo.get("full_name")
        owner, repo_name = repo_full_name.split("/")
        pr_number = pr.get("number")
        head_sha = pr.get("head", {}).get("sha")

        logger.info(
            f"Processing PR #{pr_number} from {repo_full_name}, "
            f"head: {head_sha[:7]}"
        )

        try:
            from sqlalchemy import select
            from backend.core.database import get_db
            from backend.models import User, Project

            async for db in get_db():
                result = await db.execute(
                    select(User).where(User.github_access_token.isnot(None)).limit(1)
                )
                user = result.scalar_one_or_none()

                if not user or not user.github_access_token:
                    return WebhookResponse(
                        message="No GitHub token configured",
                        status="error",
                    )

                github_client = GitHubClient(user.github_access_token)

                files = await github_client.get_pull_request_files(
                    owner, repo_name, pr_number
                )

                if not files:
                    return WebhookResponse(
                        message="No files to review",
                        status="completed",
                    )

                code_snippets = []
                for file in files[:5]:
                    if file.get("status") != "removed":
                        content = await github_client.get_file_content(
                            owner, repo_name, file["filename"], head_sha
                        )
                        if content and len(content) < 10000:
                            code_snippets.append(
                                {
                                    "filename": file["filename"],
                                    "content": content[:5000],
                                }
                            )

                if code_snippets:
                    review_task = review_code_task.delay(
                        code="\n\n".join(
                            f"# {s['filename']}\n{s['content']}"
                            for s in code_snippets
                        ),
                        language="python",
                        context={
                            "pr_number": pr_number,
                            "repo": repo_full_name,
                            "action": "webhook",
                        },
                    )

                    logger.info(f"Review task queued: {review_task.id}")

                return WebhookResponse(
                    message=f"Review started for PR #{pr_number}",
                    status="accepted",
                )
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return WebhookResponse(
                message=f"Error: {str(e)}",
                status="error",
            )

    return WebhookResponse(
        message=f"Event {x_github_event} not supported",
        status="ignored",
    )
