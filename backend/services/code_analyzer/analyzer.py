from enum import Enum
from typing import List, Dict, Any, Optional
import re


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class IssueCategory(str, Enum):
    CLEAN_CODE = "clean_code"
    SECURITY = "security"
    PERFORMANCE = "performance"
    BEST_PRACTICE = "best_practice"


class CodeIssue:
    def __init__(
        self,
        category: IssueCategory,
        severity: SeverityLevel,
        title: str,
        description: str,
        file_path: str,
        line_number: Optional[int] = None,
        code_snippet: Optional[str] = None,
        suggestion: Optional[str] = None,
        rule_id: Optional[str] = None,
    ):
        self.category = category
        self.severity = severity
        self.title = title
        self.description = description
        self.file_path = file_path
        self.line_number = line_number
        self.code_snippet = code_snippet
        self.suggestion = suggestion
        self.rule_id = rule_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "code_snippet": self.code_snippet,
            "suggestion": self.suggestion,
            "rule_id": self.rule_id,
        }


class CodeAnalyzer:
    def __init__(self, rules_config: Optional[Dict[str, Any]] = None):
        self.rules_config = rules_config or {}
        self.issues: List[CodeIssue] = []
    
    def analyze(self, file_path: str, content: str, language: str = "python") -> List[CodeIssue]:
        """Analyze code and return list of issues."""
        self.issues = []
        
        if language in ["python", "py"]:
            self._analyze_python(file_path, content)
        elif language in ["javascript", "js", "typescript", "ts"]:
            self._analyze_javascript(file_path, content)
        
        return self.issues
    
    def _analyze_python(self, file_path: str, content: str):
        """Analyze Python code for issues."""
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                self.issues.append(CodeIssue(
                    category=IssueCategory.CLEAN_CODE,
                    severity=SeverityLevel.MINOR,
                    title="Line too long",
                    description=f"Line exceeds 120 characters ({len(line)} chars)",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line[:80] + "...",
                    suggestion="Break the line into multiple lines",
                    rule_id="CC001",
                ))
            
            if len(line.strip()) == 0 and i > len(lines) - 3:
                self.issues.append(CodeIssue(
                    category=IssueCategory.CLEAN_CODE,
                    severity=SeverityLevel.INFO,
                    title="Trailing whitespace",
                    description="Line has trailing whitespace",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line,
                    suggestion="Remove trailing whitespace",
                    rule_id="CC002",
                ))
        
        if self._has_deep_nesting(lines):
            self.issues.append(CodeIssue(
                category=IssueCategory.CLEAN_CODE,
                severity=SeverityLevel.MAJOR,
                title="Deep nesting detected",
                description="Code has excessive nesting depth (>4 levels)",
                file_path=file_path,
                suggestion="Consider refactoring with early returns or extracting methods",
                rule_id="CC003",
            ))
        
        func_names = self._extract_function_names(lines)
        if len(func_names) > 20:
            self.issues.append(CodeIssue(
                category=IssueCategory.CLEAN_CODE,
                severity=SeverityLevel.MAJOR,
                title="Too many functions",
                description=f"File contains {len(func_names)} functions",
                file_path=file_path,
                suggestion="Consider splitting into multiple modules",
                rule_id="CC004",
            ))
    
    def _analyze_javascript(self, file_path: str, content: str):
        """Analyze JavaScript/TypeScript code for issues."""
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            if len(line) > 120:
                self.issues.append(CodeIssue(
                    category=IssueCategory.CLEAN_CODE,
                    severity=SeverityLevel.MINOR,
                    title="Line too long",
                    description=f"Line exceeds 120 characters ({len(line)} chars)",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line[:80] + "...",
                    suggestion="Break the line into multiple lines",
                    rule_id="CC001",
                ))
        
        console_logs = re.findall(r'console\.(log|debug|info|warn|error)', content)
        if len(console_logs) > 0:
            self.issues.append(CodeIssue(
                category=IssueCategory.BEST_PRACTICE,
                severity=SeverityLevel.MINOR,
                title="Console statements found",
                description=f"Found {len(console_logs)} console statement(s)",
                file_path=file_path,
                suggestion="Remove console statements or use proper logging",
                rule_id="BP001",
            ))
    
    def _has_deep_nesting(self, lines: List[str]) -> bool:
        max_indent = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            max_indent = max(max_indent, indent)
        return max_indent > 16
    
    def _extract_function_names(self, lines: List[str]) -> List[str]:
        func_pattern = r'^\s*def\s+(\w+)'
        funcs = []
        for line in lines:
            match = re.match(func_pattern, line)
            if match:
                funcs.append(match.group(1))
        return funcs
    
    def detect_duplicates(self, file_path: str, content: str) -> List[CodeIssue]:
        """Detect duplicate code patterns."""
        issues = []
        
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        seen = {}
        
        for i, line in enumerate(lines):
            if len(line) > 20 and line in seen:
                issues.append(CodeIssue(
                    category=IssueCategory.CLEAN_CODE,
                    severity=SeverityLevel.MAJOR,
                    title="Potential duplicate code",
                    description=f"Similar line found at line {seen[line]}",
                    file_path=file_path,
                    line_number=i + 1,
                    code_snippet=line[:60] + "...",
                    suggestion="Extract to a reusable function",
                    rule_id="CC005",
                ))
            else:
                seen[line] = i + 1
        
        return issues
