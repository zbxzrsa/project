# AI Code Quality Platform 文档

AI Code Quality Platform 是一个 AI 驱动的代码质量检查平台，通过集成大语言模型（LLM）对代码进行自动化审查，帮助开发团队提升代码质量、发现安全漏洞并遵循最佳实践。

**快速链接**: [架构](./ARCHITECTURE.md) | [接口](./INTERFACES.md) | [开发者指南](./DEVELOPER_GUIDE.md)

---

## 核心文档

### [架构](./ARCHITECTURE.md)
系统设计、技术栈、组件结构和数据流程。从这里开始了解系统如何运作。

### [接口](./INTERFACES.md)
公开 API、认证方式和数据模型。集成或使用此系统的参考。

### [开发者指南](./DEVELOPER_GUIDE.md)
环境搭建、开发工作流、编码规范和常见任务。贡献者必读。

---

## 项目概览

| 项目 | 描述 |
|------|------|
| 后端 | FastAPI (Python) - REST API 服务 |
| 前端 | Next.js (TypeScript) - 用户界面 |
| 数据库 | PostgreSQL (主数据存储) / SQLite (开发) |
| 缓存 | Redis (会话和缓存) |
| 图数据库 | Neo4j (代码关系图) |
| LLM 集成 | OpenAI / Anthropic / Ollama |

---

## 技术栈

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy (异步)
- **认证**: JWT (OAuth2PasswordBearer)
- **密码加密**: bcrypt
- **数据库**: PostgreSQL / SQLite
- **缓存**: Redis

### 前端
- **框架**: Next.js 14
- **UI**: React 18 + Tailwind CSS
- **状态管理**: Zustand
- **数据请求**: Axios + React Query
- **表单**: React Hook Form + Zod

### 基础设施
- **容器**: Docker + Docker Compose
- **LLM 提供商**: OpenAI, Anthropic Claude, Ollama (本地部署)

---

## 入门指南

### 项目新人？

按此路径学习：
1. **[架构](./ARCHITECTURE.md)** - 了解全局
2. **[接口](./INTERFACES.md)** - 学习 API
3. **[开发者指南](./DEVELOPER_GUIDE.md)** - 搭建环境

### 首次贡献？

1. **[开发者指南](./DEVELOPER_GUIDE.md)** - 搭建和工作流
2. **[常见任务](./DEVELOPER_GUIDE.md#常见任务)** - 分步指南

---

## 快速参考

### 命令

```bash
# Docker 启动所有服务
docker-compose up -d

# 后端开发
cd backend && uvicorn backend.main:app --reload

# 前端开发
cd frontend && npm run dev
```

### 重要文件

| 文件 | 目的 |
|------|------|
| `backend/main.py` | FastAPI 应用入口 |
| `backend/api/v1/` | API 路由定义 |
| `backend/services/` | 业务逻辑层 |
| `backend/models/` | SQLAlchemy 数据模型 |
| `frontend/src/lib/api.ts` | API 客户端配置 |
| `docker-compose.yml` | 容器编排配置 |
