# 需求实施计划

- [ ] 1. 设置项目结构和核心接口
  - 创建 `backend/core/security/` 目录结构
  - 创建 `backend/core/permissions/` 目录结构
  - 创建 `backend/core/rbac/` 目录结构
  - 创建 `backend/api/v1/auth/` 目录结构
  - 设置安全相关的测试框架

- [ ] 2. 实现数据模型和验证
  - [ ] 2.1 创建 User 和 UserRole 模型
    - 在 `backend/models/user.py` 中定义 User 类
    - 实现 UserRole 模型 (user_id, tenant_id, role)
    - 实现 is_superuser, is_active 字段

  - [ ] 2.2 创建 Tenant 模型
    - 定义 Tenant 类 (id, name, slug, plan)
    - 实现 is_active, plan 字段

  - [ ] 2.3 创建 APIKey 模型
    - 实现 key_hash 存储
    - 实现 expires_at, last_used_at

  - [ ] 2.4 实现 Permission 枚举
    - 定义所有权限常量
    - 实现权限到角色的映射

  - [ ]* 2.5 为数据模型编写单元测试
    - 测试 User 序列化
    - 测试 Tenant 验证
    - 测试 APIKey 哈希

- [ ] 3. 实现 Token Service
  - [ ] 3.1 实现 JWT Token 生成
    - 在 `backend/core/security/tokens.py` 实现
    - 创建 access_token (15分钟过期)
    - 创建 refresh_token (7天过期)
    - 实现 TokenPayload 定义

  - [ ] 3.2 实现 Token 验证
    - 实现 verify_token 函数
    - 实现 token 解析和过期检查

  - [ ] 3.3 实现 Token 刷新
    - 实现 refresh_access_token
    - 实现 TokenPair 返回

  - [ ]* 3.4 编写 Token Service 单元测试
    - 测试 token 生成和验证
    - 测试 token 过期处理

- [ ] 4. 实现 Password Service
  - [ ] 4.1 实现密码哈希
    - 在 `backend/core/security/passwords.py` 实现
    - 使用 bcrypt cost factor 12
    - 实现 hash_password 函数

  - [ ] 4.2 实现密码验证
    - 实现 verify_password 函数
    - 实现密码强度验证

  - [ ] 4.3 实现密码策略
    - 最少8字符
    - 至少1个大写字母
    - 至少1个小写字母
    - 至少1个数字
    - 至少1个特殊字符

  - [ ]* 4.4 编写 Password Service 单元测试
    - 测试密码哈希一致性
    - 测试密码强度验证

- [ ] 5. 实现 RBAC Service
  - [ ] 5.1 实现角色分配
    - 在 `backend/core/rbac/service.py` 实现
    - 实现 assign_role 函数
    - 实现 revoke_role 函数

  - [ ] 5.2 实现权限获取
    - 实现 get_role_permissions
    - 实现角色继承逻辑

  - [ ] 5.3 实现租户管理员检查
    - 实现 is_tenant_admin 函数
    - 实现跨租户访问控制

  - [ ]* 5.4 编写 RBAC Service 单元测试
    - 测试角色分配
    - 测试权限继承

- [ ] 6. 实现 Permission Service
  - [ ] 6.1 实现权限检查
    - 在 `backend/core/permissions/service.py` 实现
    - 实现 check_permission 函数
    - 实现 check_project_access 函数

  - [ ] 6.2 实现用户权限获取
    - 实现 get_user_permissions 函数
    - 实现权限缓存

  - [ ] 6.3 实现资源级别权限
    - 实现 READ_ARCHITECTURE_CONFIG 检查
    - 实现 READ_REPORT 检查

  - [ ]* 6.4 编写 Permission Service 单元测试
    - 测试权限检查逻辑
    - 测试资源级别权限

- [ ] 7. 实现 Authentication API
  - [ ] 7.1 实现用户注册
    - POST `/api/v1/auth/register`
    - 验证邮箱和密码
    - 创建用户并分配 Guest 角色

  - [ ] 7.2 实现用户登录
    - POST `/api/v1/auth/login`
    - 验证凭证
    - 返回 JWT Token Pair

  - [ ] 7.3 实现 Token 刷新
    - POST `/api/v1/auth/refresh`
    - 验证 refresh_token
    - 返回新的 access_token

  - [ ] 7.4 实现登出
    - POST `/api/v1/auth/logout`
    - 使 refresh_token 失效

  - [ ] 7.5 实现当前用户查询
    - GET `/api/v1/auth/me`
    - 返回当前用户信息

- [ ] 8. 实现 User API
  - [ ] 8.1 实现用户列表
    - GET `/api/v1/users` (仅管理员)
    - 支持分页和筛选

  - [ ] 8.2 实现用户详情
    - GET `/api/v1/users/{id}`
    - 返回用户信息和角色

  - [ ] 8.3 实现角色更新
    - PUT `/api/v1/users/{id}/role`
    - 分配/更新用户角色

- [ ] 9. 实现 Tenant API
  - [ ] 9.1 实现租户创建
    - POST `/api/v1/tenants` (仅超级管理员)
    - 创建租户记录

  - [ ] 9.2 实现租户查询
    - GET `/api/v1/tenants/{id}`
    - 返回租户信息

- [ ] 10. 实现中间件
  - [ ] 10.1 实现认证中间件
    - 在 `backend/core/middleware/auth.py` 实现
    - 解析 Authorization header
    - 验证 JWT token
    - 设置当前用户上下文

  - [ ] 10.2 实现权限中间件
    - 实现角色验证
    - 实现权限检查装饰器

  - [ ] 10.3 实现速率限制
    - 登录: 5次/分钟/IP
    - API: 1000次/小时/用户

- [ ] 11. 实现数据库表
  - [ ] 11.1 创建用户相关表
    - 创建 `users` 表
    - 创建 `user_roles` 表
    - 创建 `tenants` 表

  - [ ] 11.2 创建 API Key 表
    - 创建 `api_keys` 表
    - 实现密钥哈希存储

  - [ ] 11.3 创建审计日志表
    - 创建 `audit_logs` 表
    - 记录所有访问尝试

- [ ] 12. 实现 API Key 管理
  - [ ] 12.1 实现 API Key 创建
    - POST `/api/v1/api-keys`
    - 生成密钥并加密存储

  - [ ] 12.2 实现 API Key 查询
    - GET `/api/v1/api-keys`
    - 列出用户的 API Keys

  - [ ] 12.3 实现 API Key 撤销
    - DELETE `/api/v1/api-keys/{id}`
    - 使密钥失效

- [ ] 13. 实现前端认证组件
  - [ ] 13.1 创建登录页面
    - 在 `frontend/pages/auth/login.tsx` 实现
    - 实现邮箱/密码表单
    - 实现 token 存储

  - [ ] 13.2 创建注册页面
    - 在 `frontend/pages/auth/register.tsx` 实现
    - 实现用户注册表单

  - [ ] 13.3 创建用户管理页面
    - 在 `frontend/pages/admin/users.tsx` 实现
    - 实现用户列表
    - 实现角色分配

  - [ ] 13.4 创建个人设置页面
    - 在 `frontend/pages/settings/profile.tsx` 实现
    - 显示当前用户信息

  - [ ]* 13.5 编写前端认证测试
    - 测试登录流程
    - 测试权限验证

- [ ] 14. 检查点 - 确保所有功能集成正常
  - 测试完整认证流程
  - 测试基于角色的访问控制
  - 测试多租户数据隔离

- [ ] 15. 实现安全加固
  - [ ] 15.1 实现密码加密
    - API keys 加密存储
    - 实现密钥轮换

  - [ ] 15.2 实现审计日志
    - 记录所有敏感操作
    - 记录访问尝试

  - [ ] 15.3 实现账户锁定
    - 失败登录5次后锁定
    - 实现解锁机制
