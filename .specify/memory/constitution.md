<!--
Sync Impact Report:
- Version change: Initial → 1.0.0
- New principles added: 5 core principles established
- Added sections: Core Principles, Development Standards, Quality Assurance, Governance
- Templates status:
  ✅ plan-template.md - reviewed, compatible
  ✅ spec-template.md - reviewed, compatible
  ✅ tasks-template.md - reviewed, compatible
- Follow-up TODOs: None
-->

# 运动管家 Constitution

## Core Principles

### I. RESTful API 优先

每个功能必须通过清晰、一致的 RESTful API 接口暴露：

- API 设计必须遵循 REST 原则（资源导向、标准 HTTP 方法、适当的状态码）
- 所有 API 端点必须有明确的版本控制（如 `/api/v1/`）
- 请求和响应必须使用 JSON 格式，并具有清晰的数据结构
- API 文档必须与实现保持同步

**理由**：作为 API 服务，清晰一致的接口设计是客户端集成和维护的基础。

### II. 数据准确性与完整性

运动数据和健身计划的准确性不可妥协：

- 所有运动数据（步数、距离、卡路里等）必须经过验证和范围检查
- 数据库操作必须保证 ACID 特性，防止数据不一致
- 关键数据变更必须有审计日志
- 数据迁移必须经过充分测试，确保无数据丢失

**理由**：用户依赖准确的数据来追踪健身进度和健康状况，数据错误会直接影响用户体验和信任。

### III. 模块化架构

系统必须按功能域进行清晰的模块划分：

- 四大核心模块必须保持独立：健身计划管理、运动数据追踪、用户社交功能、数据分析报告
- 模块间通过明确定义的接口交互，避免直接依赖
- 每个模块必须可以独立开发、测试和部署
- 共享逻辑（如认证、日志）统一抽取到公共层

**理由**：模块化设计支持并行开发、降低耦合度，便于功能扩展和维护。

### IV. 测试驱动开发

代码质量通过测试保证，测试优先于实现：

- 核心功能必须先编写测试用例，确认测试失败后再实现
- 每个 API 端点必须有对应的集成测试
- 数据模型变更必须有相应的测试覆盖
- 关键业务逻辑必须有单元测试

**理由**：TDD 确保代码符合需求，减少回归问题，提高重构信心。

### V. 用户数据安全

保护用户隐私和健康数据是基本责任：

- 所有 API 端点必须实施认证和授权机制
- 敏感数据（如健康指标）传输必须使用 HTTPS
- 用户数据访问必须遵循最小权限原则
- 密码等敏感信息必须加密存储，不得明文记录

**理由**：运动管家处理用户的健康和个人数据，数据泄露会造成严重后果。

## Development Standards

### API 设计标准

- 使用语义化的资源命名（名词复数形式）
- 适当使用 HTTP 方法：GET（查询）、POST（创建）、PUT/PATCH（更新）、DELETE（删除）
- 返回恰当的 HTTP 状态码：2xx（成功）、4xx（客户端错误）、5xx（服务器错误）
- 实现统一的错误响应格式

### 代码组织

- 采用分层架构：Controller/API → Service → Repository/Model
- 按功能模块组织代码目录结构
- 保持单一职责原则，避免过度复杂的类或函数

### 文档要求

- API 接口必须有完整的文档（请求格式、响应格式、错误代码）
- 复杂业务逻辑必须有代码注释说明
- 数据模型必须有清晰的字段说明

## Quality Assurance

### 测试要求

- 新功能必须包含集成测试
- API 契约变更必须有对应的契约测试
- 关键计算逻辑（如卡路里计算）必须有单元测试
- 测试覆盖率目标：核心模块 ≥ 70%

### 代码审查

- 所有代码变更必须经过同行审查
- 审查时必须检查：功能正确性、测试覆盖、代码风格、安全问题
- 必须验证 Constitution 原则的遵守情况

### 性能标准

- API 响应时间：P95 < 500ms（基础要求）
- 并发支持：至少支持 100 并发用户
- 数据库查询必须有适当的索引优化

## Governance

### 修订流程

- Constitution 修订需要团队讨论和共识
- 重大原则变更（增删核心原则）需要版本号 MAJOR 升级
- 新增或扩展原则需要版本号 MINOR 升级
- 文字澄清或修正需要版本号 PATCH 升级

### 合规性审查

- 所有 Pull Request 必须验证是否符合 Constitution 原则
- 如需违反原则（如引入额外复杂性），必须在 PR 中明确说明理由和替代方案评估
- 定期审查（每季度）确保实践与 Constitution 保持一致

### 版本控制

- Constitution 变更必须记录在版本历史中
- 每次修订必须更新版本号和修订日期
- 保持向前兼容，避免破坏性变更

**Version**: 1.0.0 | **Ratified**: 2025-11-10 | **Last Amended**: 2025-11-10
