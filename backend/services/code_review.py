from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel

from backend.llm import LLMMessage, llm_router
from backend.core.logging import logger


class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CodeIssue(BaseModel):
    severity: IssueSeverity
    category: str
    title: str
    description: str
    location: Dict[str, Any]
    suggestion: Optional[str] = None
    owasp_category: Optional[str] = None
    iso_25010_category: Optional[str] = None


class CodeReviewResult(BaseModel):
    summary: str
    score: int
    issues: List[CodeIssue]
    strengths: List[str]
    improvements: List[str]


SYSTEM_PROMPT = """You are an expert code reviewer analyzing code for quality, security, and best practices.

Your task is to analyze the provided code and identify:
1. Security vulnerabilities (map to OWASP Top 10 2021)
2. Code quality issues (map to ISO/IEC 25010)
3. Performance problems
4. Code smells and anti-patterns
5. Best practices violations

For each issue found, provide:
- Severity: critical, high, medium, low, or info
- Category: security, quality, performance, maintainability, reliability
- Title: brief description
- Description: detailed explanation
- Location: file path and line numbers
- Suggestion: how to fix the issue

Provide your response in JSON format with the following structure:
{
    "summary": "Overall assessment",
    "score": 0-100 quality score,
    "issues": [
        {
            "severity": "critical|high|medium|low|info",
            "category": "security|quality|performance|maintainability|reliability",
            "title": "Issue title",
            "description": "Detailed description",
            "location": {"file": "path/to/file", "line": 123, "column": 1},
            "suggestion": "How to fix this issue",
            "owasp_category": "A01|A02|... (if security)",
            "iso_25010_category": "Functional suitability|Performance efficiency|... (if quality)"
        }
    ],
    "strengths": ["List of good practices found"],
    "improvements": ["List of suggested improvements"]
}

Only output valid JSON, no additional text."""


class CodeReviewService:
    def __init__(self):
        self.llm = llm_router

    async def review_code(
        self,
        code: str,
        language: str = "python",
        context: Optional[Dict[str, Any]] = None
    ) -> CodeReviewResult:
        user_message = f"""Please review the following {language} code:

```{language}
{code}
```

Additional context: {context or 'No additional context provided'}"""

        messages = [
            LLMMessage(role="system", content=SYSTEM_PROMPT),
            LLMMessage(role="user", content=user_message)
        ]

        try:
            response = await self.llm.generate(
                messages=messages,
                temperature=0.3,
                max_tokens=8000
            )

            return self._parse_response(response.content)

        except Exception as e:
            logger.error(f"Code review failed: {e}")
            return CodeReviewResult(
                summary=f"Code review failed: {str(e)}",
                score=0,
                issues=[],
                strengths=[],
                improvements=["Unable to complete review due to service error"]
            )

    def _parse_response(self, response_content: str) -> CodeReviewResult:
        import json
        
        try:
            data = json.loads(response_content)
            
            issues = []
            for issue_data in data.get("issues", []):
                issues.append(CodeIssue(
                    severity=IssueSeverity(issue_data.get("severity", "info")),
                    category=issue_data.get("category", "quality"),
                    title=issue_data.get("title", "Unknown issue"),
                    description=issue_data.get("description", ""),
                    location=issue_data.get("location", {}),
                    suggestion=issue_data.get("suggestion"),
                    owasp_category=issue_data.get("owasp_category"),
                    iso_25010_category=issue_data.get("iso_25010_category"),
                ))
            
            return CodeReviewResult(
                summary=data.get("summary", ""),
                score=data.get("score", 50),
                issues=issues,
                strengths=data.get("strengths", []),
                improvements=data.get("improvements", [])
            )
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM response as JSON: {response_content[:200]}")
            return CodeReviewResult(
                summary="Failed to parse review results",
                score=50,
                issues=[],
                strengths=[],
                improvements=["Unable to parse review results"]
            )


code_review_service = CodeReviewService()
