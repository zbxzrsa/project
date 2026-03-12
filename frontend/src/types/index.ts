export interface User {
  id: string;
  email: string;
  full_name: string | null;
  tenant_id: string;
  role: string;
  is_active: string;
  is_superuser: string;
  created_at: string;
  updated_at: string;
  avatar_url?: string;
}

export interface Tenant {
  id: string;
  name: string;
  settings: Record<string, unknown>;
  created_at: string;
}

export interface Project {
  id: string;
  tenant_id: string;
  name: string;
  repository_url: string | null;
  settings: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Review {
  id: string;
  project_id: string;
  commit_sha: string | null;
  status: string;
  results: Record<string, unknown> | null;
  created_at: string;
}

export interface FeatureFlag {
  id: string;
  tenant_id: string;
  name: string;
  enabled: boolean;
  rules: Record<string, unknown>;
  created_at: string;
}

export interface AuditLog {
  id: string;
  tenant_id: string;
  user_id: string;
  action: string;
  details: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Branch {
  id: string;
  name: string;
  project_id: string;
  is_default: boolean;
  last_commit_sha: string | null;
  last_commit_message: string | null;
  last_commit_author: string | null;
  last_analysis_at: string | null;
  analysis_status: string;
  issues_count: number;
  critical_issues: number;
  score: number | null;
  created_at: string;
}

export interface AnalysisTask {
  id: string;
  project_id: string;
  branch_id: string | null;
  branch_name: string;
  commit_sha: string | null;
  status: "pending" | "queued" | "processing" | "completed" | "failed";
  stage: string;
  progress: number;
  results: Record<string, unknown> | null;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
}

export interface ReviewIssue {
  id: string;
  severity: "critical" | "major" | "minor" | "info";
  category: string;
  title: string;
  description: string;
  file_path: string;
  line_number: number | null;
  suggestion: string | null;
}

export interface ProjectAnalysis {
  id: string;
  project_id: string;
  branch_name: string;
  commit_sha: string;
  score: number;
  issues: ReviewIssue[];
  strengths: string[];
  improvements: string[];
  analyzed_at: string;
}

export interface ArchitectureNode {
  id: string;
  name: string;
  type: "file" | "module" | "class" | "function";
  file_path: string;
  line_start: number | null;
  line_end: number | null;
  branches: string[];
}

export interface ArchitectureEdge {
  source: string;
  target: string;
  type: string;
}

export interface ArchitectureGraph {
  nodes: ArchitectureNode[];
  edges: ArchitectureEdge[];
  nodeCount: number;
  edgeCount: number;
}

export interface Activity {
  id: string;
  type: "review" | "project" | "analysis";
  action: string;
  description: string;
  project_name: string | null;
  created_at: string;
}

export interface DashboardStats {
  total_projects: number;
  pending_reviews: number;
  critical_issues: number;
  architecture_health: number;
}

export interface ReviewFeedback {
  id: string;
  review_id: string;
  issue_id: string | null;
  user_id: string;
  action: "accepted" | "dismissed" | "fixed";
  comment: string | null;
  created_at: string;
}

export interface ComplianceReport {
  total_issues: number;
  severity_counts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  compliance_score: number;
  issues: ComplianceIssue[];
}

export interface ComplianceIssue {
  standard: string;
  category: string;
  severity: string;
  title: string;
  description: string;
  location: Record<string, unknown>;
  remediation: string | null;
}

export interface MetricsData {
  project_count: number;
  review_stats: {
    total: number;
    completed: number;
    avg_score: number;
  };
  quality_trend: Array<{
    period: string;
    avg_score: number;
  }>;
  technical_debt: {
    total_issues: number;
    by_severity: Record<string, number>;
    estimated_hours: number;
  };
  issues_by_category: Record<string, number>;
  period_days: number;
}
