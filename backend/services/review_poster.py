from typing import Dict, Any, List
from backend.services.github_client import GitHubClient


class ReviewPoster:
    """SRS-010: Post review comments to GitHub pull requests"""
    
    def __init__(self, access_token: str):
        self.github_client = GitHubClient(access_token)
    
    async def post_review_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        commit_sha: str,
        review_results: Dict[str, Any],
    ) -> bool:
        """Post review results as comments to GitHub PR"""
        
        try:
            await self._post_summary_comment(
                owner, repo, pr_number, review_results
            )
            
            await self._post_file_comments(
                owner, repo, pr_number, commit_sha, review_results
            )
            
            return True
            
        except Exception as e:
            from backend.core.logging import logger
            logger.error(f"Error posting review comment: {e}")
            return False
    
    async def _post_summary_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        results: Dict[str, Any],
    ) -> None:
        """Post summary comment to PR"""
        
        score = results.get("score", 0)
        issues = results.get("issues", [])
        strengths = results.get("strengths", [])
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in issues:
            sev = issue.get("severity", "low")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        summary_lines = [
            "## Code Review Results",
            "",
            f"**Overall Score:** {score}/100",
            "",
            f"### Issues Summary",
            f"- 🔴 Critical: {severity_counts.get('critical', 0)}",
            f"- 🟠 High: {severity_counts.get('high', 0)}",
            f"- 🟡 Medium: {severity_counts.get('medium', 0)}",
            f"- 🟢 Low: {severity_counts.get('low', 0)}",
            "",
        ]
        
        if strengths:
            summary_lines.append("### Strengths")
            for s in strengths[:5]:
                summary_lines.append(f"- ✅ {s}")
            summary_lines.append("")
        
        summary_lines.append("_Analyzed by AI Code Quality Platform_")
        
        await self.github_client.create_pull_request_review(
            owner=owner,
            repo=repo,
            pull_number=pr_number,
            body="\n".join(summary_lines),
            event="COMMENT",
        )
    
    async def _post_file_comments(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        commit_sha: str,
        results: Dict[str, Any],
    ) -> None:
        """Post inline file comments for issues"""
        
        issues = results.get("issues", [])
        
        severity_order = ["critical", "high", "medium", "low"]
        sorted_issues = sorted(
            issues,
            key=lambda x: severity_order.index(x.get("severity", "low"))
        )
        
        for issue in sorted_issues[:10]:
            file_path = issue.get("location", {}).get("file")
            line = issue.get("location", {}).get("line")
            
            if not file_path:
                continue
            
            severity = issue.get("severity", "low")
            emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }.get(severity, "⚪")
            
            comment_body = [
                f"{emoji} **{severity.upper()}** - {issue.get('title', 'Issue')}",
                "",
                issue.get("description", ""),
            ]
            
            if issue.get("suggestion"):
                comment_body.extend(["", f"**💡 Suggestion:** {issue['suggestion']}"])
            
            if issue.get("category"):
                comment_body.extend(["", f"_Category: {issue['category']}_"])
            
            try:
                if line:
                    await self.github_client.create_pull_request_review_comment(
                        owner=owner,
                        repo=repo,
                        pull_number=pr_number,
                        body="\n".join(comment_body),
                        commit_id=commit_sha,
                        path=file_path,
                        line=line,
                    )
            except Exception:
                pass


review_poster = ReviewPoster
