# 需求实施计划

- [ ] 1. 设置项目结构和核心接口
  - 创建 `backend/services/ast_parser/` 目录结构 (Python/JS/Go/Java/Rust 解析器)
  - 创建 `backend/services/graph_storage/` 目录结构
  - 创建 `backend/services/architecture_analyzer/` 目录结构
  - 创建 `backend/services/drift_detector/` 目录结构
  - 创建 `backend/services/simulation_engine/` 目录结构
  - 设置 AST 和图分析相关的测试框架

- [ ] 2. 实现数据模型和验证
  - [ ] 2.1 创建 GraphNode 和 GraphRelationship 模型
    - 在 `backend/models/graph.py` 中定义 GraphNode 类
    - 实现 NodeType 枚举 (file, class, function, variable, module)
    - 实现 GraphRelationship 模型

  - [ ] 2.2 创建 ArchitectureBlueprint 模型
    - 定义 Layer 类 (name, allowed_layers_below, node_patterns)
    - 定义 Boundary 类 (source_pattern, target_patterns, violation_action)
    - 定义 DependencyRule 类

  - [ ] 2.3 创建 DriftAlert 模型
    - 实现 Severity 枚举
    - 实现 DriftAlert 包含规则引用和修复建议

  - [ ] 2.4 创建 RefactoringScenario 和 ImpactReport 模型
    - 定义 ScenarioType (move_function, extract_module, merge_classes)
    - 实现 ImpactReport 包含影响节点、关系变化、风险评估

  - [ ]* 2.5 为数据模型编写单元测试
    - 测试 GraphNode 序列化
    - 测试 ArchitectureBlueprint 验证
    - 测试 Boundary 规则匹配

- [ ] 3. 实现 AST Parser
  - [ ] 3.1 实现 Python AST 解析器
    - 在 `backend/services/ast_parser/python_parser.py` 实现
    - 使用 Python ast 模块
    - 使用 tree-sitter 作为补充

  - [ ] 3.2 实现 JavaScript/TypeScript 解析器
    - 在 `backend/services/ast_parser/javascript_parser.py` 实现
    - 使用 tree-sitter-javascript

  - [ ] 3.3 实现 Go 解析器
    - 在 `backend/services/ast_parser/go_parser.py` 实现
    - 使用 tree-sitter-go

  - [ ] 3.4 实现 Java 和 Rust 解析器
    - 实现 tree-sitter-java
    - 实现 tree-sitter-rust

  - [ ] 3.5 实现关系提取器
    - 实现 import/export 提取
    - 实现 function call 提取
    - 实现 class inheritance 提取
    - 实现 variable references 提取

  - [ ]* 3.6 编写 AST Parser 单元测试
    - 测试各语言解析器
    - 测试关系提取准确性

- [ ] 4. 实现 Graph Storage
  - [ ] 4.1 实现 Neo4j 连接管理
    - 在 `backend/services/graph_storage/connection.py` 实现连接池
    - 实现连接重试逻辑

  - [ ] 4.2 实现节点存储
    - 在 `backend/services/graph_storage/nodes.py` 实现节点操作
    - 实现批量节点创建
    - 实现节点查询

  - [ ] 4.3 实现关系存储
    - 实现边的创建和查询
    - 实现关系强度计算
    - 实现增量更新

  - [ ] 4.4 实现图查询接口
    - 实现依赖查询
    - 实现耦合度计算
    - 实现模块结构查询

  - [ ] 4.5 创建 Neo4j 索引
    - 创建 project_id 索引
    - 创建 fully_qualified_name 索引

  - [ ]* 4.6 编写 Graph Storage 集成测试
    - 测试大规模节点插入性能
    - 测试查询响应时间

- [ ] 5. 实现 Architecture Analyzer
  - [ ] 5.1 实现架构模式检测
    - 在 `backend/services/architecture_analyzer/pattern_detector.py` 实现
    - 检测分层架构
    - 检测 MVC 模式
    - 检测微服务边界

  - [ ] 5.2 实现架构蓝图对比
    - 在 `backend/services/architecture_analyzer/blueprint_comparator.py` 实现
    - 对比实际架构与蓝图
    - 生成 DriftReport

  - [ ] 5.3 实现耦合度计算
    - 实现耦合度指标计算
    - 生成 CouplingReport

  - [ ]* 5.4 编写 Architecture Analyzer 单元测试
    - 测试模式检测准确性
    - 测试蓝图对比逻辑

- [ ] 6. 实现 Drift Detector
  - [ ] 6.1 实现架构漂移检测
    - 在 `backend/services/drift_detector/drift_detector.py` 实现
    - 实现 DriftRule 定义
    - 实现边界违规检测

  - [ ] 6.2 实现漂移趋势分析
    - 实现时间范围查询
    - 生成 DriftTrend 列表

  - [ ] 6.3 实现实时告警
    - 实现 DriftAlert 生成
    - 实现告警严重性分级

  - [ ]* 6.4 编写 Drift Detector 单元测试
    - 测试边界违规检测
    - 测试漂移趋势计算

- [ ] 7. 实现 Simulation Engine
  - [ ] 7.1 实现重构场景模拟器
    - 在 `backend/services/simulation_engine/simulator.py` 实现
    - 实现 MoveFunctionScenario
    - 实现 ExtractModuleScenario
    - 实现 MergeClassesScenario

  - [ ] 7.2 实现影响分析
    - 计算受影响的节点
    - 计算新增和移除的关系
    - 计算依赖变化

  - [ ] 7.3 实现风险评估
    - 评估风险等级 (low, medium, high)
    - 生成警告列表

  - [ ] 7.4 实现场景比较
    - 实现 SimulationResult 比较
    - 生成 ComparisonReport

  - [ ]* 7.5 编写 Simulation Engine 单元测试
    - 测试移动函数影响分析
    - 测试模块提取影响分析

- [ ] 8. 实现 API 端点
  - [ ] 8.1 实现图数据查询 API
    - GET `/api/v1/projects/{id}/graph` - 获取项目图数据
    - GET `/api/v1/projects/{id}/graph/nodes` - 获取图节点
    - GET `/api/v1/projects/{id}/graph/edges` - 获取图边

  - [ ] 8.2 实现架构分析 API
    - GET `/api/v1/projects/{id}/architecture` - 获取架构分析报告
    - GET `/api/v1/projects/{id}/drift` - 获取漂移报告
    - GET `/api/v1/projects/{id}/drift/alerts` - 获取活跃告警

  - [ ] 8.3 实现蓝图管理 API
    - GET `/api/v1/projects/{id}/blueprint` - 获取架构蓝图
    - PUT `/api/v1/projects/{id}/blueprint` - 更新架构蓝图

  - [ ] 8.4 实现模拟 API
    - POST `/api/v1/projects/{id}/simulate` - 创建重构模拟
    - GET `/api/v1/simulations/{id}` - 获取模拟结果
    - POST `/api/v1/simulations/{id}/compare` - 比较模拟结果

- [ ] 9. 实现前端可视化
  - [ ] 9.1 实现图可视化引擎
    - 在 `frontend/components/architecture-graph/` 实现可视化组件
    - 支持 D3.js 或 React Flow

  - [ ] 9.2 实现交互式架构图
    - 实现缩放和平移
    - 实现节点筛选和搜索
    - 实现依赖高亮

  - [ ] 9.3 实现实时告警展示
    - 在 `frontend/components/drift-alerts/` 实现告警面板
    - 实现严重性颜色编码

  - [ ] 9.4 实现重构模拟预览
    - 在 `frontend/components/simulation-preview/` 实现模拟结果展示
    - 实现前后对比视图

  - [ ]* 9.5 编写前端可视化测试
    - 测试图渲染性能
    - 测试交互响应

- [ ] 10. 实现 LLM 多模型支持
  - [ ] 10.1 扩展 LLM Router
    - 支持 GPT-4
    - 支持 Claude 3.5
    - 支持 Ollama 本地模型

  - [ ] 10.2 实现模型元数据管理
    - 实现模型能力展示
    - 实现定价层级展示
    - 实现响应时间估算

  - [ ] 10.3 实现模型自动降级
    - 实现不可用时切换到默认模型

- [ ] 11. 检查点 - 确保所有功能集成正常
  - 测试 AST 解析和存储流程
  - 测试图查询性能
  - 测试可视化渲染

- [ ] 12. 实现性能优化
  - [ ] 12.1 实现图查询缓存
    - 缓存频繁查询结果
    - 实现缓存失效策略

  - [ ] 12.2 实现增量更新
    - 只更新变更的文件
    - 减少全量解析开销

  - [ ] 12.3 实现并行处理
    - 多文件并行解析
    - 并行图数据写入
