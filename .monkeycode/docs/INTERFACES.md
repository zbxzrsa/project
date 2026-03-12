# 接口文档

## 概述

AI Code Quality Platform 提供 RESTful API 接口，基于 FastAPI 构建。所有 API 遵循 JSON 格式进行请求和响应。

## Base URL

```
开发环境: http://localhost:8000/api/v1
生产环境: https://api.example.com/api/v1
```

## 认证方式

### JWT Bearer Token

API 使用 JWT (JSON Web Token) 进行身份验证。在请求头中携带 access_token：

```http
Authorization: Bearer <access_token>
```

### Token 刷新机制

当 access_token 过期时，使用 refresh_token 获取新的 token 对：

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

**响应**:
```json
{
  "access_token": "<new_access_token>",
  "refresh_token": "<new_refresh_token>"
}
```

## 公共端点

### 健康检查

```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## 认证端点

### 注册用户

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "John Doe",
  "tenant_id": null  // 可选，为 null 时自动创建租户
}
```

**响应** (201 Created):
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_active": "true",
  "is_superuser": "false",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 用户登录

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**响应**:
```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>",
  "token_type": "bearer"
}
```

### 获取当前用户信息

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_active": "true",
  "is_superuser": "false",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 请求密码重置

```http
POST /api/v1/auth/password-reset
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**响应**:
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

### 确认密码重置

```http
POST /api/v1/auth/password-reset/confirm
Content-Type: application/json

{
  "token": "<reset_token>",
  "new_password": "new_secure_password"
}
```

**响应**:
```json
{
  "id": "uuid",
  "email": "user@example.com",
  ...
}
```

## 用户管理端点

### 获取用户列表

```http
GET /api/v1/users
Authorization: Bearer <access_token>
```

### 获取用户详情

```http
GET /api/v1/users/{user_id}
Authorization: Bearer <access_token>
```

### 更新用户

```http
PATCH /api/v1/users/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "New Name"
}
```

### 删除用户

```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <access_token>
```

## 租户管理端点

### 获取租户列表

```http
GET /api/v1/tenants
Authorization: Bearer <access_token>
```

### 获取租户详情

```http
GET /api/v1/tenants/{tenant_id}
Authorization: Bearer <access_token>
```

### 创建租户

```http
POST /api/v1/tenants
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Company Name",
  "settings": {}
}
```

### 更新租户

```http
PATCH /api/v1/tenants/{tenant_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Name"
}
```

## 项目管理端点

### 获取项目列表

```http
GET /api/v1/projects
Authorization: Bearer <access_token>
```

**查询参数**:
- `tenant_id` (可选): 过滤租户下的项目

### 获取项目详情

```http
GET /api/v1/projects/{project_id}
Authorization: Bearer <access_token>
```

### 创建项目

```http
POST /api/v1/projects
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Project Name",
  "description": "Project description",
  "repository_url": "https://github.com/org/repo",
  "settings": {}
}
```

**响应** (201 Created):
```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "name": "Project Name",
  "description": "Project description",
  "repository_url": "https://github.com/org/repo",
  "settings": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 更新项目

```http
PATCH /api/v1/projects/{project_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Name"
}
```

### 删除项目

```http
DELETE /api/v1/projects/{project_id}
Authorization: Bearer <access_token>
```

## 代码审查端点

### 获取审查列表

```http
GET /api/v1/reviews
Authorization: Bearer <access_token>
```

**查询参数**:
- `project_id` (可选): 过滤项目下的审查
- `skip` (可选): 分页偏移，默认 0
- `limit` (可选): 分页限制，默认 100

### 获取审查详情

```http
GET /api/v1/reviews/{review_id}
Authorization: Bearer <access_token>
```

**响应**:
```json
{
  "id": "uuid",
  "project_id": "uuid",
  "commit_sha": "abc123",
  "branch": "main",
  "pr_number": 42,
  "status": "completed",
  "results": {
    "summary": "Overall assessment...",
    "score": 85,
    "issues": [
      {
        "severity": "high",
        "category": "security",
        "title": "SQL Injection Risk",
        "description": "...",
        "location": {"file": "src/db.py", "line": 45},
        "suggestion": "Use parameterized queries",
        "owasp_category": "A03:2021"
      }
    ],
    "strengths": ["Good error handling", "..."],
    "improvements": ["Add type hints", "..."]
  },
  "error_message": null,
  "started_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:01:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:01:00Z"
}
```

### 创建审查

```http
POST /api/v1/reviews
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "project_id": "uuid",
  "commit_sha": "abc123",
  "branch": "main",
  "pr_number": 42
}
```

### 执行代码分析

```http
POST /api/v1/reviews/{review_id}/analyze
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "code": "def hello():\n    print('Hello, World!')",
  "language": "python"
}
```

**审查状态**:
- `pending` - 等待处理
- `processing` - 正在分析
- `completed` - 分析完成
- `failed` - 分析失败

### 更新审查

```http
PATCH /api/v1/reviews/{review_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "completed"
}
```

### 删除审查

```http
DELETE /api/v1/reviews/{review_id}
Authorization: Bearer <access_token>
```

## OAuth 端点

### GitHub OAuth 登录

```http
GET /api/v1/oauth/github/login
```

重定向到 GitHub 授权页面。

### GitHub OAuth 回调

```http
GET /api/v1/oauth/github/callback?code=<auth_code>
```

**响应**:
```json
{
  "access_token": "<access_token>",
  "refresh_token": "<refresh_token>",
  "token_type": "bearer"
}
```

## 错误响应格式

### 标准错误

```json
{
  "error": "ERROR_CODE",
  "detail": "详细错误信息"
}
```

### 常见错误码

| 错误码 | HTTP 状态码 | 描述 |
|--------|-------------|------|
| UNAUTHORIZED | 401 | 未认证或 token 无效 |
| FORBIDDEN | 403 | 权限不足 |
| NOT_FOUND | 404 | 资源不存在 |
| CONFLICT | 409 | 资源冲突 |
| VALIDATION_ERROR | 422 | 请求验证失败 |
| INTERNAL_SERVER_ERROR | 500 | 服务器内部错误 |

## 速率限制

API 目前没有实施速率限制，但建议：
- 批量请求使用分页
- 避免短时间内大量请求
- 使用 WebSocket 进行实时更新（未来支持）

## 前端 API 客户端

项目提供预配置的 Axios 客户端 (`frontend/src/lib/api.ts`)：

```typescript
import { apiClient } from '@/lib/api';

// 自动处理 token 注入
// 自动处理 401 时的 token 刷新
// 自动重试失败的请求

const response = await apiClient.get('/projects');
```

### 使用示例

```typescript
// 登录
const loginResponse = await apiClient.post('/auth/login', {
  email: 'user@example.com',
  password: 'password'
});

// 获取项目列表
const projectsResponse = await apiClient.get('/projects');

// 创建审查并分析
const reviewResponse = await apiClient.post('/reviews', {
  project_id: projectId
});

await apiClient.post(`/reviews/${reviewResponse.data.id}/analyze`, {
  code: 'def example(): pass',
  language: 'python'
});
```
