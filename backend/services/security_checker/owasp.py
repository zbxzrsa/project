from typing import List, Dict, Any, Optional
import re
from backend.services.code_analyzer.analyzer import CodeIssue, IssueCategory, SeverityLevel


class SecurityChecker:
    """OWASP Top 10 and security best practices checker."""
    
    def __init__(self):
        self.issues: List[CodeIssue] = []
    
    def check(self, file_path: str, content: str, language: str = "python") -> List[CodeIssue]:
        """Run all security checks on the code."""
        self.issues = []
        
        if language in ["python", "py"]:
            self._check_python(content, file_path)
        elif language in ["javascript", "js", "typescript", "ts"]:
            self._check_javascript(content, file_path)
        
        return self.issues
    
    def _check_python(self, content: str, file_path: str):
        """Check Python code for security issues."""
        lines = content.split("\n")
        
        self._check_sql_injection(lines, file_path)
        self._check_hardcoded_secrets(content, file_path)
        self._check_eval_usage(lines, file_path)
        self._check_pickle_usage(lines, file_path)
        self._check_yaml_load(lines, file_path)
        self._check_weak_crypto(content, file_path)
        self._check_command_injection(lines, file_path)
    
    def _check_javascript(self, content: str, file_path: str):
        """Check JavaScript/TypeScript code for security issues."""
        lines = content.split("\n")
        
        self._check_xss_vulnerabilities(content, file_path)
        self._check_eval_usage(lines, file_path)
        self._check_hardcoded_secrets(content, file_path)
        self._check_weak_crypto(content, file_path)
        self._check_inner_html_usage(content, file_path)
    
    def _check_sql_injection(self, lines: List[str], file_path: str):
        """Check for SQL injection vulnerabilities."""
        dangerous_patterns = [
            (r'execute\s*\(\s*f["\'].*?\{.*?\}', 'SQL query built with f-string'),
            (r'execute\s*\(\s*["\'].*?%s.*?%', 'SQL query with string formatting'),
            (r'execute\s*\(\s*["\'].*?\+.*?\)', 'SQL query with string concatenation'),
            (r'cursor\.execute\s*\(\s*f["\']', 'SQL query built with f-string'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append(CodeIssue(
                        category=IssueCategory.SECURITY,
                        severity=SeverityLevel.CRITICAL,
                        title="Potential SQL Injection",
                        description=f"Possible SQL injection: {desc}",
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:60],
                        suggestion="Use parameterized queries or ORM",
                        rule_id="OWASP-A03-001",
                    ))
    
    def _check_xss_vulnerabilities(self, content: str, file_path: str):
        """Check for XSS vulnerabilities in JavaScript."""
        dangerous_patterns = [
            (r'innerHTML\s*=', 'Using innerHTML can lead to XSS'),
            (r'outerHTML\s*=', 'Using outerHTML can lead to XSS'),
            (r'document\.write\s*\(', 'Using document.write can lead to XSS'),
            (r'<script[^>]*>', 'Inline script tag found'),
        ]
        
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for pattern, desc in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append(CodeIssue(
                        category=IssueCategory.SECURITY,
                        severity=SeverityLevel.CRITICAL,
                        title="Potential XSS Vulnerability",
                        description=desc,
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:60],
                        suggestion="Use textContent instead of innerHTML or sanitize input",
                        rule_id="OWASP-A03-002",
                    ))
    
    def _check_hardcoded_secrets(self, content: str, file_path: str):
        """Check for hardcoded secrets."""
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret'),
            (r'token\s*=\s*["\'][^"\']{20,}["\']', 'Hardcoded token'),
            (r'private[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded private key'),
            (r'aws[_-]?access[_-]?key', 'Hardcoded AWS access key'),
            (r'ghp_[a-zA-Z0-9]{36}', 'Hardcoded GitHub token'),
            (r'xox[baprs]-[a-zA-Z0-9]{10,}', 'Hardcoded Slack token'),
        ]
        
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for pattern, desc in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append(CodeIssue(
                        category=IssueCategory.SECURITY,
                        severity=SeverityLevel.CRITICAL,
                        title="Hardcoded Secret",
                        description=desc,
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:40] + "...",
                        suggestion="Use environment variables or secrets management",
                        rule_id="OWASP-A02-001",
                    ))
    
    def _check_eval_usage(self, lines: List[str], file_path: str):
        """Check for dangerous eval usage."""
        for i, line in enumerate(lines, 1):
            if re.search(r'\beval\s*\(', line):
                self.issues.append(CodeIssue(
                    category=IssueCategory.SECURITY,
                    severity=SeverityLevel.CRITICAL,
                    title="Dangerous eval() Usage",
                    description="Using eval() can lead to code injection",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip()[:60],
                    suggestion="Avoid eval(), use safer alternatives",
                    rule_id="OWASP-A03-003",
                ))
    
    def _check_pickle_usage(self, lines: List[str], file_path: str):
        """Check for insecure pickle usage."""
        for i, line in enumerate(lines, 1):
            if re.search(r'pickle\.loads?\s*\(', line):
                self.issues.append(CodeIssue(
                    category=IssueCategory.SECURITY,
                    severity=SeverityLevel.CRITICAL,
                    title="Insecure Deserialization",
                    description="Using pickle can lead to remote code execution",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip()[:60],
                    suggestion="Use JSON or safer serialization methods",
                    rule_id="OWASP-A08-001",
                ))
    
    def _check_yaml_load(self, lines: List[str], file_path: str):
        """Check for unsafe YAML loading."""
        for i, line in enumerate(lines, 1):
            if re.search(r'yaml\.load\s*\([^,)]*(?!\s*,\s*Loader', line):
                self.issues.append(CodeIssue(
                    category=IssueCategory.SECURITY,
                    severity=SeverityLevel.CRITICAL,
                    title="Unsafe YAML Loading",
                    description="yaml.load without Loader can execute arbitrary code",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip()[:60],
                    suggestion="Use yaml.safe_load() or yaml.load with Loader",
                    rule_id="OWASP-A08-002",
                ))
    
    def _check_weak_crypto(self, content: str, file_path: str):
        """Check for weak cryptographic algorithms."""
        weak_algos = [
            (r'md5\s*\(', 'MD5 is cryptographically broken'),
            (r'sha1\s*\(', 'SHA-1 is cryptographically weak'),
            (r'DES\s*\(', 'DES is cryptographically weak'),
            (r'RC4\s*\(', 'RC4 is cryptographically weak'),
        ]
        
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            for pattern, desc in weak_algos:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append(CodeIssue(
                        category=IssueCategory.SECURITY,
                        severity=SeverityLevel.MAJOR,
                        title="Weak Cryptographic Algorithm",
                        description=desc,
                        file_path=file_path,
                        line_number=i,
                        suggestion="Use stronger algorithms like SHA-256 or AES",
                        rule_id="OWASP-A02-002",
                    ))
    
    def _check_command_injection(self, lines: List[str], file_path: str):
        """Check for command injection vulnerabilities."""
        dangerous_patterns = [
            (r'os\.system\s*\(', 'os.system can lead to command injection'),
            (r'subprocess\.call\s*\([^,)]*(?!\s*shell\s*=\s*False)', 'subprocess without shell=False'),
            (r'subprocess\.run\s*\([^,)]*(?!\s*shell\s*=\s*False', 'subprocess without shell=False'),
            (r'os\.popen\s*\(', 'os.popen can lead to command injection'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, desc in dangerous_patterns:
                if re.search(pattern, line):
                    self.issues.append(CodeIssue(
                        category=IssueCategory.SECURITY,
                        severity=SeverityLevel.CRITICAL,
                        title="Potential Command Injection",
                        description=desc,
                        file_path=file_path,
                        line_number=i,
                        code_snippet=line.strip()[:60],
                        suggestion="Use subprocess with shell=False and pass arguments as list",
                        rule_id="OWASP-A01-001",
                    ))
    
    def _check_inner_html_usage(self, content: str, file_path: str):
        """Check for innerHTML usage in React."""
        lines = content.split("\n")
        
        for i, line in enumerate(lines, 1):
            if 'dangerouslySetInnerHTML' in line:
                self.issues.append(CodeIssue(
                    category=IssueCategory.SECURITY,
                    severity=SeverityLevel.MAJOR,
                    title="Dangerously Set Inner HTML",
                    description="Using dangerouslySetInnerHTML can lead to XSS",
                    file_path=file_path,
                    line_number=i,
                    code_snippet=line.strip()[:60],
                    suggestion="Sanitize content before using dangerouslySetInnerHTML",
                    rule_id="OWASP-A03-004",
                ))
