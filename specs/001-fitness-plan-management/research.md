# Technical Research: 健身计划管理

**Feature**: 健身计划管理
**Date**: 2025-11-10
**Phase**: Phase 0 - Research & Technology Selection

## Overview

本文档记录针对健身计划管理功能的技术选型研究，解决实施计划中标记的所有 NEEDS CLARIFICATION 问题。

## Research Questions

### 1. Language & Framework Selection

#### Decision: Python 3.11+ with FastAPI

**Rationale**:
- **快速开发**: FastAPI 提供自动 API 文档（OpenAPI/Swagger）、数据验证（Pydantic）和异步支持
- **类型安全**: Python 3.11+ 的类型提示 + Pydantic 提供编译时和运行时验证
- **性能**: FastAPI 基于 Starlette 和 Uvicorn，性能接近 Node.js，满足 P95 < 500ms 要求
- **生态系统**: 丰富的库支持（SQLAlchemy ORM、APScheduler 任务调度、pytest 测试）
- **学习曲线**: Python 语法简洁，团队上手快

**Alternatives Considered**:
- **Node.js + Express**: 性能优秀但缺少内置类型系统，需额外集成 TypeScript
- **Go + Gin**: 性能最佳但开发效率较低，对复杂业务逻辑支持不如 Python
- **Java + Spring Boot**: 企业级成熟但重量级，初期项目过度工程化

**Implementation Notes**:
- 使用 FastAPI 0.104+
- Python 3.11+ (性能提升 10-60%)
- Uvicorn 作为 ASGI 服务器
- 支持异步数据库操作（减少 I/O 阻塞）

---

### 2. Database & ORM

#### Decision: PostgreSQL 15+ with SQLAlchemy 2.0

**Rationale**:
- **关系型数据**: 健身计划、锻炼项目、提醒设置之间有明确的关系（一对多、多对多）
- **ACID 保证**: 符合 Constitution 的"数据准确性与完整性"原则
- **JSON 支持**: PostgreSQL 的 JSONB 类型可存储灵活的锻炼项目属性
- **索引能力**: 支持复合索引、部分索引，优化计划列表查询性能
- **SQLAlchemy**: 成熟的 ORM，支持异步操作（asyncpg）、迁移管理（Alembic）

**Alternatives Considered**:
- **MongoDB**: NoSQL 灵活性高但缺少事务保证，不符合数据完整性要求
- **MySQL**: 功能相似但 JSON 支持不如 PostgreSQL，社区活跃度较低
- **SQLite**: 轻量级但不支持高并发，不适合生产环境

**Implementation Notes**:
- PostgreSQL 15+（性能优化，JSON 查询改进）
- SQLAlchemy 2.0（异步 ORM）
- asyncpg 驱动（高性能异步 PostgreSQL 客户端）
- Alembic 用于数据库迁移

**Schema Design Considerations**:
- 使用外键约束确保引用完整性
- 为常用查询字段（user_id, status, created_at）添加索引
- 软删除策略（deleted_at 字段）保留数据审计

---

### 3. Task Scheduling (Reminders)

#### Decision: APScheduler + Redis (Persistent Job Store)

**Rationale**:
- **APScheduler**: Python 原生任务调度库，支持 Cron 表达式、间隔调度、持久化
- **Redis Job Store**: 提醒任务持久化到 Redis，服务重启后任务不丢失
- **高精度**: 支持秒级调度，满足提醒准时送达率 ≥ 98% 要求
- **可扩展**: 后期可迁移到 Celery + RabbitMQ 实现分布式任务队列

**Alternatives Considered**:
- **Celery + RabbitMQ**: 功能强大但初期复杂度过高，增加运维成本
- **Cron Jobs**: 精度不足（分钟级），无法实现秒级提醒
- **Database Polling**: 简单但性能差，不满足 100 并发用户要求

**Implementation Notes**:
- APScheduler 3.10+ with AsyncIOScheduler
- Redis 7+ 作为 Job Store 和缓存层
- 提醒任务结构：
  - 任务 ID: `reminder_{plan_id}_{user_id}`
  - 触发器: CronTrigger（基于用户设定的提醒时间）
  - Job 数据: plan_id, user_id, notification_content

**Notification Delivery**:
- 使用 Firebase Cloud Messaging (FCM) 发送移动端推送
- 使用 Web Push API 发送浏览器通知
- 失败重试机制：3次重试，指数退避（1s, 2s, 4s）

---

### 4. Testing Strategy

#### Decision: pytest + httpx + pytest-asyncio

**Rationale**:
- **pytest**: Python 标准测试框架，生态丰富，支持参数化测试、fixture 复用
- **httpx**: 异步 HTTP 客户端，与 FastAPI 的 TestClient 集成
- **pytest-asyncio**: 支持异步测试函数，测试异步 API 和服务

**Testing Layers**:

**Contract Tests** (API 接口契约):
- 工具: Schemathesis（基于 OpenAPI 规范自动生成测试）
- 覆盖: 所有 API 端点的请求/响应格式验证
- 位置: `tests/contract/test_plans_api_contract.py`

**Integration Tests** (业务流程集成):
- 工具: pytest + TestClient + 测试数据库（PostgreSQL in Docker）
- 覆盖: 完整用户场景（创建计划 → 编辑 → 设置提醒 → 删除）
- 位置: `tests/integration/test_plan_crud.py`, `test_plan_reminders.py`

**Unit Tests** (业务逻辑单元):
- 工具: pytest + unittest.mock（模拟数据库和外部服务）
- 覆盖: Service 层逻辑、数据验证、边界条件
- 位置: `tests/unit/test_plan_service.py`, `test_validators.py`

**Coverage Goal**: 核心模块 ≥ 70%（符合 Constitution 要求）

**Alternatives Considered**:
- **unittest**: Python 内置但语法冗长，fixture 管理不如 pytest
- **nose**: 已停止维护，社区推荐迁移到 pytest

**Implementation Notes**:
- pytest-cov 用于代码覆盖率报告
- pytest-xdist 用于并行测试（加速 CI/CD）
- Factory Boy 用于测试数据生成（避免硬编码）

---

### 5. Authentication & Authorization

#### Decision: JWT (JSON Web Tokens) with RS256

**Rationale**:
- **无状态**: JWT 不需要服务端存储会话，支持水平扩展
- **标准化**: RFC 7519 标准，与移动端/前端集成简单
- **安全**: RS256 (RSA签名) 比 HS256 更安全，私钥不暴露给客户端
- **性能**: 验证快速，满足 API 响应时间要求

**Implementation Strategy**:
- **Access Token**: 短期有效（15分钟），包含 user_id, permissions
- **Refresh Token**: 长期有效（7天），用于刷新 Access Token
- **Token 存储**: Refresh Token 存储在 Redis，支持撤销
- **中间件**: FastAPI Dependency Injection 实现认证中间件

**Authorization Rules**:
- 用户只能访问自己的健身计划（通过 user_id 过滤）
- 每个 API 端点验证 Token 有效性和用户权限

**Alternatives Considered**:
- **Session-based Auth**: 需要服务端存储，扩展性差
- **OAuth2 (Third-party)**: 初期无需第三方登录，复杂度过高

**Implementation Notes**:
- python-jose 库（JWT 生成和验证）
- passlib + bcrypt（密码哈希）
- Token 过期时间可配置（环境变量）

---

### 6. API Documentation & Validation

#### Decision: FastAPI 自动文档 + Pydantic 模型

**Rationale**:
- **自动生成**: FastAPI 基于 Pydantic 模型自动生成 OpenAPI 3.0 文档
- **交互式 UI**: Swagger UI (/docs) 和 ReDoc (/redoc) 开箱即用
- **类型验证**: Pydantic 提供请求/响应数据验证，减少手动检查
- **一致性**: 文档与代码同步，避免文档过期

**Documentation Standards** (符合 Constitution "Development Standards"):
- API 路径: `/api/v1/plans/*`
- 版本控制: URL 路径版本化（v1, v2）
- 错误响应: 统一格式 `{"detail": "error message", "code": "ERROR_CODE"}`
- 状态码标准:
  - 200 OK - 成功
  - 201 Created - 资源创建成功
  - 400 Bad Request - 请求参数错误
  - 401 Unauthorized - 未认证
  - 403 Forbidden - 无权限
  - 404 Not Found - 资源不存在
  - 500 Internal Server Error - 服务器错误

**Implementation Notes**:
- Pydantic BaseModel 定义所有请求/响应模型
- 使用 Field() 添加字段描述和验证规则
- 自定义异常处理器统一错误响应格式

---

### 7. Deployment & Infrastructure

#### Decision: Docker + Docker Compose (初期) → Kubernetes (扩展期)

**Rationale**:
- **Docker**: 容器化确保环境一致性（开发、测试、生产）
- **Docker Compose**: 本地开发和小规模部署简单快速
- **迁移路径**: 后期可平滑迁移到 Kubernetes 实现高可用和自动扩展

**Services Architecture**:
```yaml
services:
  api:          # FastAPI 应用
  db:           # PostgreSQL 数据库
  redis:        # Redis (Job Store + Cache)
  nginx:        # 反向代理（生产环境）
```

**Alternatives Considered**:
- **直接 Kubernetes**: 初期复杂度过高，团队学习成本大
- **Serverless (AWS Lambda)**: 有状态任务调度不适合 Serverless

**Implementation Notes**:
- Multi-stage Docker 构建（减小镜像体积）
- Health check 端点 `/health`（监控和负载均衡）
- 环境变量管理（.env 文件，不提交到 Git）

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.11+ | 主编程语言 |
| Framework | FastAPI | 0.104+ | Web 框架 |
| ASGI Server | Uvicorn | 0.24+ | 应用服务器 |
| Database | PostgreSQL | 15+ | 关系型数据库 |
| ORM | SQLAlchemy | 2.0+ | 对象关系映射 |
| DB Driver | asyncpg | 0.29+ | 异步数据库驱动 |
| Migration | Alembic | 1.12+ | 数据库迁移 |
| Task Scheduler | APScheduler | 3.10+ | 任务调度 |
| Cache/Job Store | Redis | 7+ | 缓存和任务持久化 |
| Testing | pytest | 7.4+ | 测试框架 |
| HTTP Client | httpx | 0.25+ | 异步 HTTP 客户端 |
| Auth | python-jose | 3.3+ | JWT 处理 |
| Validation | Pydantic | 2.4+ | 数据验证 |
| Container | Docker | 24+ | 容器化 |

---

## Performance Considerations

### Database Optimization
- **索引策略**: 为 user_id, status, created_at 添加复合索引
- **查询优化**: 使用 JOIN FETCH 避免 N+1 查询
- **连接池**: SQLAlchemy 连接池（pool_size=10, max_overflow=20）

### API Performance
- **异步处理**: 所有 I/O 操作（数据库、Redis）使用异步
- **响应缓存**: 计划列表缓存 30 秒（Redis）
- **分页**: 计划列表默认分页（page_size=20）

### Reminder Performance
- **批量调度**: APScheduler 批量添加提醒任务（减少 Redis 往返）
- **过期清理**: 定期清理已触发的提醒任务（每日凌晨）

---

## Security Considerations

### API Security
- **HTTPS Only**: 生产环境强制 HTTPS
- **CORS**: 配置允许的源（移动端/Web 端）
- **Rate Limiting**: slowapi 库（每用户 100 req/min）
- **SQL Injection**: SQLAlchemy 参数化查询（自动防护）

### Data Security
- **密码哈希**: bcrypt + salt（cost factor=12）
- **敏感数据**: 不记录用户健康数据到日志
- **Token 安全**: Access Token 短期，Refresh Token 可撤销

---

## Development Workflow

### Local Setup
```bash
# 1. 克隆仓库
git clone <repo> && cd my-project

# 2. 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务（Docker Compose）
docker-compose up -d

# 5. 运行迁移
alembic upgrade head

# 6. 启动开发服务器
uvicorn src.main:app --reload
```

### Testing
```bash
# 运行所有测试
pytest

# 运行特定测试层
pytest tests/unit
pytest tests/integration
pytest tests/contract

# 代码覆盖率
pytest --cov=src --cov-report=html
```

---

## Next Steps

Phase 0 研究完成，所有 NEEDS CLARIFICATION 已解决。

**Proceed to Phase 1**:
1. 生成 data-model.md（实体关系模型）
2. 生成 API contracts（OpenAPI 规范）
3. 生成 quickstart.md（开发者快速入门）
4. 更新 agent context（技术栈信息）

**Constitution Re-check**: ✅ 所选技术栈符合所有原则
- RESTful API: FastAPI 支持 ✅
- 数据准确性: PostgreSQL + SQLAlchemy ✅
- 模块化: 分层架构 ✅
- TDD: pytest 生态 ✅
- 数据安全: JWT + bcrypt ✅
