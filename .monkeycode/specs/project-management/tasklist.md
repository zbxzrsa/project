# 需求实施计划

- [ ] 1. 设置项目结构和核心接口
  - 创建 `backend/services/project_service/` 目录结构
  - 创建 `backend/services/task_service/` 目录结构
  - 创建 `backend/services/queue_manager/` 目录结构
  - 创建 `backend/services/repo_connector/` 目录结构
  - 创建 `backend/core/websocket/` 目录结构
  - 设置项目管理和任务相关的测试框架

- [ ] 2. 实现数据模型和验证
  - [ ] 2.1 创建 Project 模型
    - 在 `backend/models/project.py` 中定义 Project 类
    - 实现 tenant_id, repository_url, is_public 字段
    - 实现 ProjectSettings 嵌套模型

  - [ ] 2.2 创建 AnalysisTask 模型
    - 定义 TaskStatus 枚举 (pending, queued, processing, completed, failed, cancelled)
    - 定义 TaskStage 枚举 (queued, fetching, parsing, analyzing, generating_report, completed)
    - 实现 TaskResult 和 TaskError

  - [ ] 2.3 创建 TaskProgress 模型
    - 实现 stage_progress 映射
    - 实现 elapsed_time 计算

  - [ ] 2.4 创建 RepoConnection 模型
    - 定义 RepoProvider 枚举 (github, gitlab, bitbucket)
    - 实现连接状态管理

  - [ ]* 2.5 为数据模型编写单元测试
    - 测试 Project 序列化
    - 测试 Task 状态转换
    - 测试 TaskProgress 计算

- [ ] 3. 实现 Project Service
  - [ ] 3.1 实现项目 CRUD
    - 在 `backend/services/project_service/crud.py` 实现
    - create_project
    - get_project
    - list_projects (支持筛选和排序)
    - update_project
    - delete_project

  - [ ] 3.2 实现项目指标
    - 实现 get_project_metrics
    - 计算 total_issues, critical_issues 等
    - 计算 trend 趋势

  - [ ] 3.3 实现项目筛选
    - 支持按状态筛选
    - 支持按日期范围筛选
    - 支持按仓库筛选

  - [ ]* 3.4 编写 Project Service 单元测试
    - 测试项目 CRUD 操作
    - 测试项目筛选逻辑

- [ ] 4. 实现 Task Service
  - [ ] 4.1 实现任务生命周期管理
    - 在 `backend/services/task_service/lifecycle.py` 实现
    - 创建任务 (pending 状态)
    - 取消任务
    - 重试失败任务

  - [ ] 4.2 实现任务状态转换
    - pending -> queued
    - queued -> processing
    - processing -> completed/failed
    - 实现状态转换验证

  - [ ] 4.3 实现任务进度跟踪
    - 实现 get_task_progress
    - 计算 elapsed_time
    - 估算剩余时间

  - [ ] 4.4 实现任务列表查询
    - 支持按状态筛选
    - 支持按项目筛选
    - 支持按日期范围筛选
    - 支持分页 (1000+ 任务)

  - [ ]* 4.5 编写 Task Service 单元测试
    - 测试任务状态转换
    - 测试任务取消逻辑
    - 测试重试机制

- [ ] 5. 实现 Queue Manager
  - [ ] 5.1 实现队列操作
    - 在 `backend/services/queue_manager/queue.py` 实现
    - enqueue_task (支持优先级)
    - dequeue_task
    - get_queue_status

  - [ ] 5.2 实现队列管理
    - 实现队列重排序
    - 实现队列暂停/恢复
    - 实现队列大小限制 (1000)

  - [ ] 5.3 实现队列统计
    - waiting_count
    - processing_count
    - completed_today
    - failed_today
    - average_wait_time

  - [ ] 5.4 实现 Redis 集成
    - 使用 Redis 存储队列
    - 实现分布式锁
    - 实现任务持久化

  - [ ]* 5.5 编写 Queue Manager 集成测试
    - 测试入队/出队性能
    - 测试队列暂停/恢复

- [ ] 6. 实现 Repository Connector
  - [ ] 6.1 实现 GitHub 连接
    - 在 `backend/services/repo_connector/github.py` 实现
    - 使用 OAuth 或 Personal Access Token
    - 验证仓库访问权限

  - [ ] 6.2 实现 GitLab 连接
    - 在 `backend/services/repo_connector/gitlab.py` 实现
    - 验证仓库访问权限

  - [ ] 6.3 实现 Bitbucket 连接
    - 在 `backend/services/repo_connector/bitbucket.py` 实现
    - 验证仓库访问权限

  - [ ] 6.4 实现仓库同步
    - 实现 sync_repository
    - 获取最新代码
    - 触发分析任务

  - [ ] 6.5 实现连接验证
    - 验证连接有效性
    - 检查仓库权限

  - [ ]* 6.6 编写 Repository Connector 单元测试
    - 测试 GitHub 连接
    - 测试仓库同步

- [ ] 7. 实现 WebSocket Hub
  - [ ] 7.1 实现任务状态广播
    - 在 `backend/core/websocket/hub.py` 实现
    - broadcast_task_update
    - broadcast_queue_update

  - [ ] 7.2 实现订阅管理
    - subscribe (user_id, project_id)
    - unsubscribe (connection_id)

  - [ ] 7.3 实现实时更新
    - 任务状态变化推送
    - 队列状态变化推送

  - [ ]* 7.4 编写 WebSocket 集成测试
    - 测试连接管理
    - 测试消息广播

- [ ] 8. 实现 Project API
  - [ ] 8.1 实现项目 CRUD 端点
    - POST `/api/v1/projects` - 创建项目
    - GET `/api/v1/projects` - 列出项目
    - GET `/api/v1/projects/{id}` - 获取项目详情
    - PUT `/api/v1/projects/{id}` - 更新项目
    - DELETE `/api/v1/projects/{id}` - 删除项目

  - [ ] 8.2 实现项目指标端点
    - GET `/api/v1/projects/{id}/metrics` - 获取项目指标

- [ ] 9. 实现 Task API
  - [ ] 9.1 实现任务管理端点
    - POST `/api/v1/tasks` - 创建分析任务
    - GET `/api/v1/tasks` - 列出任务
    - GET `/api/v1/tasks/{id}` - 获取任务详情
    - POST `/api/v1/tasks/{id}/cancel` - 取消任务
    - POST `/api/v1/tasks/{id}/retry` - 重试任务

  - [ ] 9.2 实现任务进度端点
    - GET `/api/v1/tasks/{id}/progress` - 获取任务进度

- [ ] 10. 实现 Queue API
  - [ ] 10.1 实现队列管理端点
    - GET `/api/v1/queue/status` - 获取队列状态
    - POST `/api/v1/queue/pause` - 暂停队列
    - POST `/api/v1/queue/resume` - 恢复队列

- [ ] 11. 实现 Repository API
  - [ ] 11.1 实现仓库连接端点
    - GET `/api/v1/repos` - 列出已连接仓库
    - POST `/api/v1/repos/connect` - 连接仓库
    - POST `/api/v1/repos/{id}/disconnect` - 断开连接
    - POST `/api/v1/repos/{id}/sync` - 同步仓库

- [ ] 12. 实现前端仪表板
  - [ ] 12.1 创建项目仪表板页面
    - 在 `frontend/pages/dashboard/` 实现
    - 显示项目列表
    - 显示项目指标

  - [ ] 12.2 实现筛选和排序
    - 按状态筛选
    - 按日期范围筛选
    - 按名称/更新时间排序

  - [ ] 12.3 实现统计摘要
    - 总项目数
    - 活跃分析数
    - 关键问题数

  - [ ]* 12.4 编写仪表板测试
    - 测试数据加载性能
    - 测试筛选功能

- [ ] 13. 实现前端任务管理
  - [ ] 13.1 创建任务列表页面
    - 在 `frontend/pages/tasks/` 实现
    - 显示任务状态
    - 显示进度百分比

  - [ ] 13.2 创建任务详情页面
    - 在 `frontend/pages/tasks/[id].tsx` 实现
    - 显示当前阶段
    - 显示执行日志

  - [ ] 13.3 实现实时进度
    - 使用 WebSocket
    - 实现阶段进度条

  - [ ]* 13.4 编写任务管理测试
    - 测试任务创建
    - 测试状态更新

- [ ] 14. 实现前端仓库管理
  - [ ] 14.1 创建仓库连接页面
    - 在 `frontend/pages/repos/` 实现
    - 实现 OAuth 授权流程
    - 实现 Token 输入

  - [ ] 14.2 实现仓库列表
    - 显示已连接仓库
    - 显示同步状态

  - [ ]* 14.3 编写仓库管理测试
    - 测试连接流程

- [ ] 15. 实现队列管理前端
  - [ ] 15.1 创建队列监控页面
    - 在 `frontend/pages/admin/queue.tsx` 实现
    - 显示队列状态
    - 显示等待/处理中数量

  - [ ] 15.2 实现队列控制
    - 暂停/恢复按钮
    - 任务重排序

- [ ] 16. 检查点 - 确保所有功能集成正常
  - 测试端到端任务流程
  - 测试 WebSocket 实时更新
  - 测试仓库连接

- [ ] 17. 实现性能优化
  - [ ] 17.1 实现仪表板缓存
    - 缓存项目列表
    - 实现缓存失效

  - [ ] 17.2 实现分页优化
    - 支持大量任务分页
    - 实现游标分页

- [ ] 18. 实现可靠性
  - [ ] 18.1 实现任务持久化
    - 任务状态保存到数据库
    - 系统重启后恢复

  - [ ] 18.2 实现失败恢复
    - 自动重试失败任务
    - 最多3次重试

  - [ ] 18.3 实现后台 Worker
    - 使用 Celery 或类似
    - 自动恢复处理中的任务
