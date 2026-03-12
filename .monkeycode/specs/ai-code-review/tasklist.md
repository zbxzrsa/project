# 需求实施计划

- [ ] 1. 设置项目结构和核心接口
  - 创建 `backend/services/webhook_handler/` 目录结构
  - 创建 `backend/services/code_analyzer/` 目录结构
  - 创建 `backend/services/security_checker/` 目录结构
  - 创建 `backend/services/review_generator/` 目录结构
  - 设置 webhook 和分析相关的测试框架

- [ ] 2. 实现数据模型和验证
  - [ ] 2.1 创建 ReviewRequest 和 FileChange 模型
    - 在 `backend/models/review.py` 中定义 ReviewRequest 类
    - 实现 FileChange 模型支持 added/modified/deleted 状态
    - 实现文件内容的 diff 提取逻辑

  - [ ] 2.2 创建 AnalysisResult 和 CodeIssue 模型
    - 定义 SeverityLevel 枚举 (critical, major, minor, info)
    - 定义 IssueCategory 枚举 (clean_code, security, performance, best_practice)
    - 实现 CodeIssue 模型包含位置信息和修复建议

  - [ ] 2.3 创建 ProjectRuleConfig 模型
    - 定义 enabled_categories 配置
    - 实现 severity_thresholds 映射
    - 实现 disabled_rules 列表

  - [ ]* 2.4 为数据模型编写单元测试
    - 测试 ReviewRequest 序列化/反序列化
    - 测试 FileChange 状态转换
    - 测试 CodeIssue 严重性分级

- [ ] 3. 实现 Webhook Handler
  - [ ] 3.1 实现 GitHub Webhook 接收端点
    - 在 `backend/api/v1/webhooks.py` 创建 POST `/api/v1/webhooks/github`
    - 实现 push event 解析
    - 实现 pull request event 解析

  - [ ] 3.2 实现 Webhook 签名验证
    - 实现 HMAC SHA256 签名验证
    - 验证 webhook_secret 配置
    - 返回 401 当签名无效时

  - [ ] 3.3 实现 Webhook 配置管理
    - 创建 POST `/api/v1/webhooks/github/configure`
    - 实现 webhook_secret 生成
    - 实现 webhook_id 存储

  - [ ]* 3.4 编写 Webhook Handler 单元测试
    - 测试 push event 解析
    - 测试 pull request 解析
    - 测试 HMAC 签名验证

- [ ] 4. 实现 Code Analyzer
  - [ ] 4.1 创建 CodeAnalyzer 服务
    - 在 `backend/services/code_analyzer/analyzer.py` 实现分析器
    - 集成 LLM Router 进行代码分析
    - 实现 Clean Code 违规检测 (SRP, DRY, 命名规范, 函数大小限制)

  - [ ] 4.2 实现 ISO/IEC 25010 质量属性检查
    - 功能适宜性检查
    - 性能效率检查
    - 兼容性检查
    - 可用性检查
    - 可靠性检查
    - 可维护性检查
    - 可移植性检查

  - [ ] 4.3 实现 Code Smell 检测
    - 检测重复代码
    - 检测过长函数
    - 检测过深嵌套
    - 检测全局变量使用

  - [ ]* 4.4 编写 Code Analyzer 集成测试
    - 测试多种语言的代码分析
    - 测试 Clean Code 违规检测准确性

- [ ] 5. 实现 Security Checker
  - [ ] 5.1 实现 OWASP Top 10 检查
    - 在 `backend/services/security_checker/owasp.py` 实现检查器
    - SQL 注入检测
    - XSS 漏洞检测
    - CSRF 漏洞检测
    - 认证缺陷检测
    - 不安全反序列化检测
    - XXE 检测
    - 访问控制缺陷检测
    - 安全配置错误检测

  - [ ] 5.2 实现 CVE 参考关联
    - 建立漏洞类型到 CVE 的映射
    - 实现 CVEInfo 查询接口

  - [ ] 5.3 实现 Google Style Guide 检查
    - 安全相关约定检查
    - 代码风格检查

  - [ ]* 5.4 编写 Security Checker 单元测试
    - 测试 OWASP 漏洞检测
    - 测试 CVE 引用生成

- [ ] 6. 实现 NLG Review Generator
  - [ ] 6.1 实现 Review 报告生成
    - 在 `backend/services/review_generator/generator.py` 实现生成器
    - 生成自然语言问题描述
    - 生成受影响文件和行号信息
    - 生成严重性分级说明
    - 生成可操作的修复步骤

  - [ ] 6.2 实现多格式输出
    - JSON API 响应格式
    - Markdown 报告格式
    - GitHub Comment 格式

  - [ ] 6.3 实现问题优先级排序
    - 按严重性排序
    - 生成问题摘要

  - [ ]* 6.4 编写 NLG Generator 单元测试
    - 测试不同格式输出
    - 测试问题优先级排序

- [ ] 7. 实现 LLM 集成
  - [ ] 7.1 实现 LLM Router
    - 在 `backend/services/llm/router.py` 实现路由器
    - 支持 OpenAI GPT-4
    - 支持 Anthropic Claude 3.5
    - 支持 Ollama 本地模型

  - [ ] 7.2 实现 Provider Failover
    - 实现主provider失败时自动切换
    - 实现最大重试次数控制
    - 实现 rate limit 处理

  - [ ] 7.3 实现多模型支持配置
    - 实现 per-project LLM provider 选择
    - 实现模型元数据展示

  - [ ]* 7.4 编写 LLM Router 单元测试
    - 测试 provider 切换逻辑
    - 测试 rate limit 处理

- [ ] 8. 实现数据库持久化
  - [ ] 8.1 创建数据库表
    - 创建 `reviews` 表
    - 创建 `review_issues` 表
    - 创建 `webhook_configs` 表

  - [ ] 8.2 实现 Review 仓储
    - 在 `backend/repositories/review_repository.py` 实现仓储
    - 实现 reviews CRUD 操作
    - 实现 review_issues CRUD 操作

  - [ ] 8.3 实现 Webhook Config 仓储
    - 实现 webhook 配置管理
    - 实现配置验证

- [ ] 9. 实现 API 端点
  - [ ] 9.1 实现 Review 查询 API
    - GET `/api/v1/reviews/{id}` - 获取审查结果
    - GET `/api/v1/reviews/{id}/status` - 获取审查状态

  - [ ] 9.2 实现项目规则配置 API
    - GET `/api/v1/projects/{id}/rules` - 获取项目分析规则
    - PUT `/api/v1/projects/{id}/rules` - 更新项目分析规则

- [ ] 10. 实现前端组件
  - [ ] 10.1 创建 Webhook 配置页面
    - 在 `frontend/components/webhook-config/` 创建配置表单
    - 实现 webhook URL 展示
    - 实现 secret 复制功能

  - [ ] 10.2 创建 Review 结果展示页面
    - 在 `frontend/components/review-results/` 创建结果列表
    - 实现按严重性筛选
    - 实现问题详情展开

  - [ ] 10.3 创建项目规则配置页面
    - 在 `frontend/components/rule-config/` 创建配置表单
    - 实现规则开关
    - 实现阈值配置

  - [ ]* 10.4 编写前端组件测试
    - 测试 Webhook 配置表单
    - 测试 Review 结果筛选

- [ ] 11. 检查点 - 确保所有功能集成正常
  - 测试端到端 webhook 流程
  - 测试多 provider failover
  - 测试数据库持久化

- [ ] 12. 实现性能优化
  - [ ] 12.1 实现分析缓存
    - 缓存相同代码的分析结果
    - 实现缓存失效策略

  - [ ] 12.2 实现异步处理
    - Webhook 响应与分析解耦
    - 使用后台任务队列处理分析

- [ ] 13. 实现安全加固
  - [ ] 13.1 实现 API Key 加密
    - LLM provider keys 加密存储
    - 实现密钥轮换

  - [ ] 13.2 实现请求限流
    - Webhook 端点限流
    - 分析请求限流
