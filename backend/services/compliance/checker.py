from typing import List, Dict, Any, Optional
from enum import Enum


class ComplianceStandard(str, Enum):
    ISO_25010 = "iso_25010"
    ISO_23396 = "iso_23396"
    GOOGLE_STYLE = "google_style"


class ComplianceCategory(str, Enum):
    FUNCTIONAL_SUITABILITY = "functional_suitability"
    RELIABILITY = "reliability"
    USABILITY = "usability"
    EFFICIENCY = "efficiency"
    MAINTAINABILITY = "maintainability"
    PORTABILITY = "portability"
    SECURITY = "security"


class ComplianceIssue:
    def __init__(
        self,
        standard: str,
        category: str,
        severity: str,
        title: str,
        description: str,
        location: Optional[Dict[str, Any]] = None,
        remediation: Optional[str] = None,
    ):
        self.standard = standard
        self.category = category
        self.severity = severity
        self.title = title
        self.description = description
        self.location = location or {}
        self.remediation = remediation
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "standard": self.standard,
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "remediation": self.remediation,
        }


class ComplianceChecker:
    """System shall verify compliance with ISO/IEC 25010, ISO/IEC 23396, and Google Style Guides"""
    
    def __init__(self):
        self.issues: List[ComplianceIssue] = []
    
    def check_iso_25010(self, code: str, language: str = "python") -> List[ComplianceIssue]:
        """Verify compliance with ISO/IEC 25010 software quality standards"""
        self.issues = []
        
        if language == "python":
            self._check_functional_suitability_python(code)
            self._check_reliability_python(code)
            self._check_efficiency_python(code)
            self._check_maintainability_python(code)
        
        return self.issues
    
    def _check_functional_suitability_python(self, code: str) -> None:
        """Check functional suitability - program behaves as specified"""
        import re
        
        func_pattern = r'def\s+(\w+)\s*\([^)]*\)\s*:'
        funcs = re.findall(func_pattern, code)
        
        if len(funcs) > 50:
            self.issues.append(ComplianceIssue(
                standard="ISO/IEC 25010",
                category="Functional Suitability",
                severity="medium",
                title="Excessive Function Count",
                description=f"Found {len(funcs)} functions. Consider modularization.",
                remediation="Split into multiple modules or classes"
            ))
        
        for match in re.finditer(r'def\s+(\w+)\s*\([^)]*\)\s*:\s*"""', code):
            if not match.group(0).strip().endswith('"""'):
                self.issues.append(ComplianceIssue(
                    standard="ISO/IEC 25010",
                    category="Functional Suitability",
                    severity="low",
                    title="Missing Docstring",
                    description=f"Function '{match.group(1)}' lacks proper documentation",
                    remediation="Add docstring explaining function purpose"
                ))
    
    def _check_reliability_python(self, code: str) -> None:
        """Check reliability - fault tolerance and recoverability"""
        import re
        
        dangerous_patterns = [
            (r'except:\s*$', 'Bare except clause'),
            (r'pass\s*$', 'Empty except handler'),
        ]
        
        for pattern, desc in dangerous_patterns:
            if re.search(pattern, code, re.MULTILINE):
                self.issues.append(ComplianceIssue(
                    standard="ISO/IEC 25010",
                    category="Reliability",
                    severity="high",
                    title=f"Reliability Issue: {desc}",
                    description=f"Code contains unreliable error handling",
                    remediation="Use specific exception types"
                ))
    
    def _check_efficiency_python(self, code: str) -> None:
        """Check efficiency - resource consumption"""
        import re
        
        inefficient_patterns = [
            (r'for\s+.*\s+in\s+.*:\s*\n\s*for\s+', 'Nested loops may cause performance issues'),
            (r'\.append\(.*\)\s+in\s+', 'Use list comprehension instead'),
        ]
        
        for pattern, desc in inefficient_patterns:
            if re.search(pattern, code):
                self.issues.append(ComplianceIssue(
                    standard="ISO/IEC 25010",
                    category="Efficiency",
                    severity="medium",
                    title="Performance Issue",
                    description=desc,
                    remediation="Optimize the code pattern"
                ))
    
    def _check_maintainability_python(self, code: str) -> None:
        """Check maintainability - analysability, modifiability"""
        import re
        
        lines = code.split('\n')
        for i, line in enumerate(lines):
            if len(line) > 120:
                self.issues.append(ComplianceIssue(
                    standard="ISO/IEC 25010",
                    category="Maintainability",
                    severity="low",
                    title="Line Too Long",
                    description=f"Line {i+1} exceeds 120 characters ({len(line)} chars)",
                    location={"line": i+1},
                    remediation="Break into multiple lines"
                ))
        
        for match in re.finditer(r'^[ ]+def\s+(\w+)', code, re.MULTILINE):
            indent = len(match.start())
            if indent > 16:
                self.issues.append(ComplianceIssue(
                    standard="ISO/IEC 25010",
                    category="Maintainability",
                    severity="medium",
                    title="Excessive Nesting",
                    description=f"Function '{match.group(1)}' has excessive indentation",
                    remediation="Refactor with early returns"
                ))
    
    def check_iso_23396(self, code: str, language: str = "python") -> List[ComplianceIssue]:
        """Verify compliance with ISO/IEC 23396 architectural standards"""
        self.issues = []
        
        if language == "python":
            self._check_layered_architecture(code)
            self._check_separation_of_concerns(code)
            self._check_interface_contracts(code)
            self._check_architectural_antipatterns(code)
        
        return self.issues
    
    def _check_layered_architecture(self, code: str) -> None:
        """Validate layered architecture"""
        import re
        
        patterns = {
            r'from\s+\w+\.(models|schema)': 'Data layer dependency',
            r'from\s+\w+\.(api|controller)': 'Controller in wrong layer',
            r'import\s+logging': 'Logging should be abstracted',
        }
        
        for pattern, desc in patterns.items():
            if re.search(pattern, code):
                self.issues.append(ComplianceIssue(
                    standard="ISO/IEC 23396",
                    category="Layered Architecture",
                    severity="high",
                    title="Layer Violation",
                    description=desc,
                    remediation="Follow layered architecture pattern"
                ))
    
    def _check_separation_of_concerns(self, code: str) -> None:
        """Check separation of concerns"""
        import re
        
        large_class = re.findall(r'class\s+(\w+)', code)
        
        class_bodies = {}
        for match in re.finditer(r'class\s+(\w+).*?:(.*?)(?=^class|\Z)', code, re.DOTALL | re.MULTILINE):
            class_name = match.group(1)
            body = match.group(2)
            method_count = len(re.findall(r'def\s+', body))
            class_bodies[class_name] = method_count
        
        for class_name, count in class_bodies.items():
            if count > 20:
                self.issues.append(ComplianceIssue(
                    standard="ISO/IEC 23396",
                    category="Separation of Concerns",
                    severity="medium",
                    title="God Class Detected",
                    description=f"Class '{class_name}' has {count} methods",
                    remediation="Split into smaller, focused classes"
                ))
    
    def _check_interface_contracts(self, code: str) -> None:
        """Verify interface contracts"""
        import re
        
        for match in re.finditer(r'def\s+(\w+)\s*\(([^)]*)\)\s*->\s*(\w+):', code):
            params = match.group(2)
            if '...' in params or 'None' in params:
                pass
            elif not params.strip():
                self.issues.append(ComplianceIssue(
                    standard="ISO/IEC 23396",
                    category="Interface Contracts",
                    severity="low",
                    title="Implicit Interface",
                    description=f"Function '{match.group(1)}' lacks type hints",
                    remediation="Add type hints for parameters and return"
                ))
    
    def _check_architectural_antipatterns(self, code: str) -> None:
        """Report architectural anti-patterns"""
        import re
        
        antipatterns = [
            (r'global\s+\w+', 'Global Variable'),
            (r'from\s+\.\.\s+import', 'Relative Import (circular dependency risk)'),
        ]
        
        for pattern, title in antipatterns:
            if re.search(pattern, code):
                self.issues.append(ComplianceIssue(
                    standard="ISO/IEC 23396",
                    category="Architectural Anti-patterns",
                    severity="high",
                    title=title,
                    description=f"Code contains {title}",
                    remediation="Refactor to avoid anti-pattern"
                ))
    
    def check_google_style(self, code: str, language: str = "python") -> List[ComplianceIssue]:
        """Verify compliance with Google Style Guides"""
        self.issues = []
        
        if language == "python":
            self._check_pep8(code)
            self._check_naming_conventions(code)
            self._check_documentation_requirements(code)
        
        return self.issues
    
    def _check_pep8(self, code: str) -> None:
        """Check PEP 8 compliance"""
        import re
        
        for i, line in enumerate(code.split('\n')):
            if line.rstrip() != line.rstrip():
                self.issues.append(ComplianceIssue(
                    standard="Google Style Guide",
                    category="PEP 8",
                    severity="low",
                    title="Trailing Whitespace",
                    description="Line has trailing whitespace",
                    location={"line": i+1}
                ))
            
            if line and not line[0].isspace() and len(line) > 79:
                self.issues.append(ComplianceIssue(
                    standard="Google Style Guide",
                    category="PEP 8",
                    severity="low",
                    title="Line Too Long",
                    description=f"Line exceeds 79 characters ({len(line)} chars)",
                    location={"line": i+1}
                ))
    
    def _check_naming_conventions(self, code: str) -> None:
        """Check naming conventions"""
        import re
        
        for match in re.finditer(r'def\s+([a-z][a-zA-Z0-9_]*)\s*\(', code):
            name = match.group(1)
            if name.lower() != name:
                self.issues.append(ComplianceIssue(
                    standard="Google Style Guide",
                    category="Naming Conventions",
                    severity="low",
                    title="Function Name Case",
                    description=f"Function '{name}' should be snake_case",
                    remediation="Use snake_case for function names"
                ))
        
        for match in re.finditer(r'class\s+([a-z][a-zA-Z0-9_]*)\s*\(', code):
            name = match.group(1)
            if name[0].islower():
                self.issues.append(ComplianceIssue(
                    standard="Google Style Guide",
                    category="Naming Conventions",
                    severity="low",
                    title="Class Name Case",
                    description=f"Class '{name}' should use CapWords",
                    remediation="Use CapWords for class names"
                ))
    
    def _check_documentation_requirements(self, code: str) -> None:
        """Check documentation requirements"""
        import re
        
        for match in re.finditer(r'class\s+(\w+)(?:\([^)]*\))?:', code):
            class_def = match.group(0)
            if '"""' not in class_def and "'''" not in class_def:
                self.issues.append(ComplianceIssue(
                    standard="Google Style Guide",
                    category="Documentation",
                    severity="low",
                    title="Missing Class Docstring",
                    description=f"Class '{match.group(1)}' lacks docstring",
                    remediation="Add docstring to class"
                ))
    
    def generate_compliance_report(
        self,
        code: str,
        standards: List[str],
        language: str = "python"
    ) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""
        all_issues = []
        
        if "iso_25010" in standards:
            all_issues.extend(self.check_iso_25010(code, language))
        
        if "iso_23396" in standards:
            all_issues.extend(self.check_iso_23396(code, language))
        
        if "google_style" in standards:
            all_issues.extend(self.check_google_style(code, language))
        
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for issue in all_issues:
            severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
        
        return {
            "total_issues": len(all_issues),
            "severity_counts": severity_counts,
            "issues": [i.to_dict() for i in all_issues],
            "compliance_score": max(0, 100 - (severity_counts.get("critical", 0) * 10 + 
                                                 severity_counts.get("high", 0) * 5 + 
                                                 severity_counts.get("medium", 0) * 2)),
        }


compliance_checker = ComplianceChecker()
