from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from backend.models import Project, Review, User


class MetricsCalculator:
    """Calculate code quality metrics for dashboard"""
    
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def calculate_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Calculate comprehensive metrics for the dashboard"""
        
        project_count = await self._get_project_count()
        
        review_stats = await self._get_review_stats(days)
        
        quality_trend = await self._get_quality_trend(days)
        
        technical_debt = await self._calculate_technical_debt()
        
        issues_by_category = await self._get_issues_by_category()
        
        return {
            "project_count": project_count,
            "review_stats": review_stats,
            "quality_trend": quality_trend,
            "technical_debt": technical_debt,
            "issues_by_category": issues_by_category,
            "period_days": days,
        }
    
    async def _get_project_count(self) -> int:
        result = await self.db.execute(
            select(func.count(Project.id)).where(
                Project.tenant_id == self.tenant_id
            )
        )
        return result.scalar() or 0
    
    async def _get_review_stats(self, days: int) -> Dict[str, Any]:
        since = datetime.utcnow() - timedelta(days=days)
        
        result = await self.db.execute(
            select(func.count(Review.id))
            .join(Project, Review.project_id == Project.id)
            .where(
                and_(
                    Project.tenant_id == self.tenant_id,
                    Review.created_at >= since
                )
            )
        )
        total_reviews = result.scalar() or 0
        
        completed_result = await self.db.execute(
            select(func.count(Review.id))
            .join(Project, Review.project_id == Project.id)
            .where(
                and_(
                    Project.tenant_id == self.tenant_id,
                    Review.status == "completed",
                    Review.created_at >= since
                )
            )
        )
        completed = completed_result.scalar() or 0
        
        avg_score_result = await self.db.execute(
            select(func.avg(Review.results['score']))
            .join(Project, Review.project_id == Project.id)
            .where(
                and_(
                    Project.tenant_id == self.tenant_id,
                    Review.status == "completed",
                    Review.created_at >= since
                )
            )
        )
        avg_score = avg_score_result.scalar() or 0
        
        return {
            "total": total_reviews,
            "completed": completed,
            "avg_score": round(float(avg_score), 1) if avg_score else 0,
        }
    
    async def _get_quality_trend(self, days: int) -> List[Dict[str, Any]]:
        """Get quality trend over time"""
        trend = []
        for i in range(days, 0, -7):
            since = datetime.utcnow() - timedelta(days=i)
            until = since + timedelta(days=7)
            
            result = await self.db.execute(
                select(func.avg(Review.results['score']))
                .join(Project, Review.project_id == Project.id)
                .where(
                    and_(
                        Project.tenant_id == self.tenant_id,
                        Review.status == "completed",
                        Review.created_at >= since,
                        Review.created_at < until
                    )
                )
            )
            avg = result.scalar()
            trend.append({
                "period": f"Day {i-7+1}-{i}",
                "avg_score": round(float(avg), 1) if avg else 0,
            })
        
        return trend
    
    async def _calculate_technical_debt(self) -> Dict[str, Any]:
        """Calculate technical debt metrics"""
        result = await self.db.execute(
            select(Review.results)
            .join(Project, Review.project_id == Project.id)
            .where(
                and_(
                    Project.tenant_id == self.tenant_id,
                    Review.status == "completed"
                )
            )
            .order_by(Review.created_at.desc())
            .limit(100)
        )
        
        reviews = result.scalars().all()
        
        total_issues = 0
        by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for r in reviews:
            if r and isinstance(r, dict):
                issues = r.get("issues", [])
                for issue in issues:
                    total_issues += 1
                    sev = issue.get("severity", "low")
                    by_severity[sev] = by_severity.get(sev, 0) + 1
        
        return {
            "total_issues": total_issues,
            "by_severity": by_severity,
            "estimated_hours": total_issues * 0.5,
        }
    
    async def _get_issues_by_category(self) -> Dict[str, int]:
        """Get issues grouped by category"""
        result = await self.db.execute(
            select(Review.results)
            .join(Project, Review.project_id == Project.id)
            .where(
                and_(
                    Project.tenant_id == self.tenant_id,
                    Review.status == "completed"
                )
            )
            .limit(100)
        )
        
        reviews = result.scalars().all()
        
        categories = {}
        for r in reviews:
            if r and isinstance(r, dict):
                issues = r.get("issues", [])
                for issue in issues:
                    cat = issue.get("category", "unknown")
                    categories[cat] = categories.get(cat, 0) + 1
        
        return categories


class ReportExporter:
    """Export dashboard reports in various formats"""
    
    @staticmethod
    def export_csv(metrics: Dict[str, Any]) -> str:
        """Export metrics as CSV"""
        lines = ["Metric,Value"]
        
        stats = metrics.get("review_stats", {})
        lines.append(f"Total Reviews,{stats.get('total', 0)}")
        lines.append(f"Completed Reviews,{stats.get('completed', 0)}")
        lines.append(f"Average Score,{stats.get('avg_score', 0)}")
        
        td = metrics.get("technical_debt", {})
        lines.append(f"Total Issues,{td.get('total_issues', 0)}")
        lines.append(f"Critical Issues,{td.get('by_severity', {}).get('critical', 0)}")
        lines.append(f"High Issues,{td.get('by_severity', {}).get('high', 0)}")
        lines.append(f"Estimated Hours,{td.get('estimated_hours', 0)}")
        
        return "\n".join(lines)
    
    @staticmethod
    def export_markdown(metrics: Dict[str, Any]) -> str:
        """Export metrics as Markdown"""
        lines = [
            "# Code Quality Metrics Report",
            "",
            f"**Period:** Last {metrics.get('period_days', 30)} days",
            "",
            "## Overview",
            "",
            f"- Total Projects: {metrics.get('project_count', 0)}",
            f"- Total Reviews: {metrics.get('review_stats', {}).get('total', 0)}",
            f"- Average Score: {metrics.get('review_stats', {}).get('avg_score', 0)}",
            "",
            "## Technical Debt",
            "",
            f"- Total Issues: {metrics.get('technical_debt', {}).get('total_issues', 0)}",
            f"- Critical: {metrics.get('technical_debt', {}).get('by_severity', {}).get('critical', 0)}",
            f"- High: {metrics.get('technical_debt', {}).get('by_severity', {}).get('high', 0)}",
            f"- Medium: {metrics.get('technical_debt', {}).get('by_severity', {}).get('medium', 0)}",
            f"- Low: {metrics.get('technical_debt', {}).get('by_severity', {}).get('low', 0)}",
            f"- Estimated Hours to Fix: {metrics.get('technical_debt', {}).get('estimated_hours', 0)}",
            "",
            "## Issues by Category",
            "",
        ]
        
        categories = metrics.get("issues_by_category", {})
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {cat}: {count}")
        
        lines.append("")
        lines.append("## Quality Trend (Weekly)")
        lines.append("")
        
        trend = metrics.get("quality_trend", [])
        for t in trend:
            lines.append(f"- {t.get('period')}: Score {t.get('avg_score', 0)}")
        
        return "\n".join(lines)
    
    @staticmethod
    def export_json(metrics: Dict[str, Any]) -> str:
        """Export metrics as JSON"""
        import json
        return json.dumps(metrics, indent=2)
