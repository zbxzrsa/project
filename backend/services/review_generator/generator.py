from typing import List, Dict, Any
from backend.services.code_analyzer.analyzer import CodeIssue, SeverityLevel


class ReviewGenerator:
    """Generate human-readable review reports from code issues."""
    
    def __init__(self):
        self.severity_weights = {
            SeverityLevel.CRITICAL: 4,
            SeverityLevel.MAJOR: 3,
            SeverityLevel.MINOR: 2,
            SeverityLevel.INFO: 1,
        }
    
    def generate_report(
        self,
        issues: List[CodeIssue],
        file_count: int = 0,
    ) -> Dict[str, Any]:
        """Generate a comprehensive review report."""
        
        sorted_issues = self._sort_by_severity(issues)
        
        report = {
            "summary": self._generate_summary(sorted_issues, file_count),
            "issues": [issue.to_dict() for issue in sorted_issues],
            "statistics": self._generate_statistics(sorted_issues),
            "recommendations": self._generate_recommendations(sorted_issues),
        }
        
        return report
    
    def generate_markdown(
        self,
        issues: List[CodeIssue],
        file_count: int = 0,
    ) -> str:
        """Generate a markdown-formatted review report."""
        
        sorted_issues = self._sort_by_severity(issues)
        stats = self._generate_statistics(sorted_issues)
        
        md = []
        md.append("# Code Review Report\n")
        md.append(f"**Files Analyzed:** {file_count}")
        md.append(f"**Total Issues Found:** {len(issues)}\n")
        
        md.append("## Summary\n")
        md.append(f"- Critical: {stats['critical']}")
        md.append(f"- Major: {stats['major']}")
        md.append(f"- Minor: {stats['minor']}")
        md.append(f"- Info: {stats['info']}\n")
        
        if sorted_issues:
            md.append("## Issues\n")
            
            by_category = {}
            for issue in sorted_issues:
                cat = issue.category.value
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(issue)
            
            for category, cat_issues in by_category.items():
                md.append(f"### {category.replace('_', ' ').title()}\n")
                
                for issue in cat_issues:
                    severity_emoji = self._get_severity_emoji(issue.severity)
                    md.append(f"{severity_emoji} **{issue.title}**\n")
                    md.append(f"> {issue.description}\n")
                    md.append(f"- File: `{issue.file_path}`")
                    if issue.line_number:
                        md.append(f"- Line: {issue.line_number}")
                    if issue.suggestion:
                        md.append(f"- Suggestion: {issue.suggestion}")
                    if issue.rule_id:
                        md.append(f"- Rule: `{issue.rule_id}`")
                    md.append("")
        
        return "\n".join(md)
    
    def generate_github_comment(
        self,
        issues: List[CodeIssue],
    ) -> str:
        """Generate a GitHub PR comment."""
        
        sorted_issues = self._sort_by_severity(issues)
        
        if not sorted_issues:
            return "✅ No issues found in this code review."
        
        stats = self._generate_statistics(sorted_issues)
        
        comment = []
        comment.append("## Code Review Results\n")
        comment.append(f"**Issues Found:** {len(issues)} | 🔴 {stats['critical']} | 🟠 {stats['major']} | 🟡 {stats['minor']} | ℹ️ {stats['info']}\n")
        
        critical_issues = [i for i in sorted_issues if i.severity == SeverityLevel.CRITICAL]
        if critical_issues:
            comment.append("### 🚨 Critical Issues\n")
            for issue in critical_issues[:5]:
                comment.append(f"- **{issue.title}** in `{issue.file_path}`")
                if issue.line_number:
                    comment[-1] += f":L{issue.line_number}"
                if issue.suggestion:
                    comment.append(f"  > {issue.suggestion}")
            if len(critical_issues) > 5:
                comment.append(f"- ... and {len(critical_issues) - 5} more critical issues")
            comment.append("")
        
        major_issues = [i for i in sorted_issues if i.severity == SeverityLevel.MAJOR]
        if major_issues:
            comment.append("### ⚠️ Major Issues\n")
            for issue in major_issues[:3]:
                comment.append(f"- **{issue.title}** in `{issue.file_path}`")
                if issue.suggestion:
                    comment.append(f"  > {issue.suggestion}")
            if len(major_issues) > 3:
                comment.append(f"- ... and {len(major_issues) - 3} more issues")
            comment.append("")
        
        comment.append("_Full report available in the dashboard_")
        
        return "\n".join(comment)
    
    def _sort_by_severity(self, issues: List[CodeIssue]) -> List[CodeIssue]:
        """Sort issues by severity."""
        return sorted(
            issues,
            key=lambda x: self.severity_weights.get(x.severity, 0),
            reverse=True,
        )
    
    def _generate_summary(self, issues: List[CodeIssue], file_count: int) -> str:
        """Generate a summary of the review."""
        if not issues:
            return f"Great job! No issues found in {file_count} files."
        
        stats = self._generate_statistics(issues)
        
        if stats['critical'] > 0:
            return f"Found {stats['critical']} critical issues that need immediate attention."
        elif stats['major'] > 0:
            return f"Found {stats['major']} major issues that should be addressed."
        else:
            return f"Found {stats['minor'] + stats['info']} minor issues and suggestions."
    
    def _generate_statistics(self, issues: List[CodeIssue]) -> Dict[str, int]:
        """Generate statistics about the issues."""
        return {
            "critical": len([i for i in issues if i.severity == SeverityLevel.CRITICAL]),
            "major": len([i for i in issues if i.severity == SeverityLevel.MAJOR]),
            "minor": len([i for i in issues if i.severity == SeverityLevel.MINOR]),
            "info": len([i for i in issues if i.severity == SeverityLevel.INFO]),
            "total": len(issues),
        }
    
    def _generate_recommendations(self, issues: List[CodeIssue]) -> List[str]:
        """Generate recommendations based on issues found."""
        recommendations = []
        
        critical_count = len([i for i in issues if i.severity == SeverityLevel.CRITICAL])
        security_count = len([i for i in issues if i.category.value == "security"])
        
        if critical_count > 0:
            recommendations.append(
                f"Address {critical_count} critical issue(s) before merging this code."
            )
        
        if security_count > 0:
            recommendations.append(
                "Review security issues carefully - they may expose vulnerabilities."
            )
        
        if not recommendations:
            recommendations.append("Code looks good! Consider addressing minor suggestions.")
        
        return recommendations
    
    def _get_severity_emoji(self, severity: SeverityLevel) -> str:
        """Get emoji for severity level."""
        return {
            SeverityLevel.CRITICAL: "🔴",
            SeverityLevel.MAJOR: "🟠",
            SeverityLevel.MINOR: "🟡",
            SeverityLevel.INFO: "ℹ️",
        }.get(severity, "ℹ️")
