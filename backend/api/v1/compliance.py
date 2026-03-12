from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.services.compliance.checker import compliance_checker


router = APIRouter(prefix="/compliance", tags=["Compliance"])


class ComplianceCheckRequest(BaseModel):
    code: str
    language: str = "python"
    standards: List[str] = ["iso_25010", "iso_23396", "google_style"]


class ComplianceIssueResponse(BaseModel):
    standard: str
    category: str
    severity: str
    title: str
    description: str
    location: dict
    remediation: Optional[str]


class ComplianceReportResponse(BaseModel):
    total_issues: int
    severity_counts: dict
    compliance_score: int
    issues: List[ComplianceIssueResponse]


@router.post("/check", response_model=ComplianceReportResponse)
async def check_compliance(request: ComplianceCheckRequest):
    """SRS-015, SRS-016, SRS-017: Verify compliance with ISO 25010, ISO 23396, Google Style"""
    
    report = compliance_checker.generate_compliance_report(
        code=request.code,
        standards=request.standards,
        language=request.language,
    )
    
    return ComplianceReportResponse(
        total_issues=report["total_issues"],
        severity_counts=report["severity_counts"],
        compliance_score=report["compliance_score"],
        issues=[
            ComplianceIssueResponse(**issue)
            for issue in report["issues"]
        ],
    )


@router.get("/standards")
async def list_standards():
    """List available compliance standards"""
    return {
        "standards": [
            {
                "id": "iso_25010",
                "name": "ISO/IEC 25010",
                "description": "Software quality standards",
                "categories": [
                    "Functional Suitability",
                    "Reliability",
                    "Usability",
                    "Efficiency",
                    "Maintainability",
                    "Portability",
                ],
            },
            {
                "id": "iso_23396",
                "name": "ISO/IEC 23396",
                "description": "Software architecture standards",
                "categories": [
                    "Layered Architecture",
                    "Separation of Concerns",
                    "Interface Contracts",
                    "Architectural Anti-patterns",
                ],
            },
            {
                "id": "google_style",
                "name": "Google Style Guide",
                "description": "Code style and conventions",
                "categories": [
                    "PEP 8",
                    "Naming Conventions",
                    "Documentation",
                ],
            },
        ]
    }
