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
