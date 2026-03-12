import asyncio
from typing import Dict, Any, Optional
from celery import Task
from celery.utils.log import get_task_logger

from backend.celery_app import celery_app
from backend.services.code_review import code_review_service, CodeReviewResult
from backend.core.logging import logger


logger = get_task_logger(__name__)


class ReviewTask(Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600
    retry_kwargs = {"max_retries": 3}

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.error(f"Review task {task_id} failed: {exc}")
        return super().on_failure(exc, task_id, args, kwargs, einfo)


@celery_app.task(bind=True, base=ReviewTask, name="backend.tasks.review_code")
def review_code_task(
    self,
    code: str,
    language: str = "python",
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    logger.info(f"Starting code review task for language: {language}")

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(
        code_review_service.review_code(code, language, context)
    )

    return {
        "summary": result.summary,
        "score": result.score,
        "issues": [
            {
                "severity": issue.severity.value,
                "category": issue.category,
                "title": issue.title,
                "description": issue.description,
                "location": issue.location,
                "suggestion": issue.suggestion,
                "owasp_category": issue.owasp_category,
                "iso_25010_category": issue.iso_25010_category,
            }
            for issue in result.issues
        ],
        "strengths": result.strengths,
        "improvements": result.improvements,
    }


@celery_app.task(bind=True, base=ReviewTask, name="backend.tasks.review_files")
def review_files_task(
    self,
    files: Dict[str, str],
    project_id: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    logger.info(f"Starting multi-file review for project: {project_id}")

    all_issues = []
    strengths = []
    improvements = []
    total_score = 0
    file_count = 0

    for file_path, code in files.items():
        language = _detect_language(file_path)
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            code_review_service.review_code(code, language, context)
        )

        all_issues.extend(
            {
                **issue.model_dump(),
                "file": file_path,
            }
            for issue in result.issues
        )
        strengths.extend(result.strengths)
        improvements.extend(result.improvements)
        total_score += result.score
        file_count += 1

    avg_score = total_score // file_count if file_count > 0 else 0

    return {
        "project_id": project_id,
        "summary": f"Reviewed {file_count} files",
        "score": avg_score,
        "issues": all_issues,
        "strengths": list(set(strengths)),
        "improvements": list(set(improvements)),
        "files_count": file_count,
    }


def _detect_language(file_path: str) -> str:
    extension = file_path.split(".")[-1].lower()
    language_map = {
        "py": "python",
        "js": "javascript",
        "ts": "typescript",
        "jsx": "javascript",
        "tsx": "typescript",
        "java": "java",
        "go": "go",
        "rs": "rust",
        "cpp": "cpp",
        "c": "c",
        "rb": "ruby",
        "php": "php",
        "cs": "csharp",
    }
    return language_map.get(extension, "text")
