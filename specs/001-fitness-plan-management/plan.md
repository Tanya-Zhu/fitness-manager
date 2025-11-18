# Implementation Plan: 健身计划管理

**Branch**: `001-fitness-plan-management` | **Date**: 2025-11-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-fitness-plan-management/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

本功能实现运动管家的核心模块之一：健身计划管理系统。用户可以创建个性化的健身计划（包含多个锻炼项目、执行频率和时间安排），管理现有计划（查看、编辑、删除、暂停/恢复），并接收基于计划的定时提醒通知。

核心价值：帮助用户建立和维持规律的健身习惯，通过定制化计划和及时提醒提高健身坚持度。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, SQLAlchemy 2.0, APScheduler 3.10+, Pydantic 2.4+
**Storage**: PostgreSQL 15+ with asyncpg driver, Redis 7+ (for job store and cache)
**Testing**: pytest 7.4+, httpx 0.25+, pytest-asyncio, Schemathesis (contract tests)
**Target Platform**: Linux server（云端部署，支持容器化）
**Project Type**: single（API 服务单体架构）
**Performance Goals**: API 响应时间 P95 < 500ms，支持 100 并发用户（基于 constitution 基础要求）
**Constraints**:
- 提醒通知准时送达率 ≥ 98%（误差 ±2分钟）
- 计划列表加载时间 < 2秒（支持至少 20 个计划）
- 需支持推送通知集成（移动端/Web 端）
**Scale/Scope**:
- 预期用户规模：初期 1000-10000 用户
- 每用户平均 3-5 个活动计划
- 每计划平均 5-10 个锻炼项目

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. RESTful API 优先 ✅
- **符合**: 本功能将设计符合 REST 原则的 API 端点
- **验证点**: 所有计划管理操作（CRUD）将映射到标准 HTTP 方法
- **待设计**: API 版本路径（/api/v1/），JSON 请求/响应格式

### II. 数据准确性与完整性 ✅
- **符合**: 计划和锻炼项目数据需要验证规则（名称非空、项目至少一个）
- **验证点**: 数据库事务确保计划-项目-提醒关联的一致性
- **待设计**: 数据验证逻辑、审计日志记录策略

### III. 模块化架构 ✅
- **符合**: 健身计划管理作为独立模块，通过 API 暴露
- **验证点**: 不依赖其他模块（运动数据追踪、社交、数据分析）
- **待设计**: 模块内部分层架构（Controller → Service → Repository）

### IV. 测试驱动开发 ✅
- **符合**: 将遵循 TDD 流程，先编写测试
- **验证点**: API 端点测试、业务逻辑单元测试
- **待设计**: 测试策略（单元测试覆盖率目标、集成测试范围）

### V. 用户数据安全 ✅
- **符合**: API 需要认证和授权机制
- **验证点**: 用户只能访问自己的健身计划
- **待设计**: 认证方案（JWT/Session）、权限验证中间件

**Gate Status**: ✅ PASS - 所有原则均符合，无需复杂性豁免

## Project Structure

### Documentation (this feature)

```text
specs/001-fitness-plan-management/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (already exists)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── fitness-plans-api.yaml
├── checklists/          # Quality checklists
│   └── requirements.md  # Requirements checklist (already exists)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   ├── fitness_plan.py
│   ├── exercise.py
│   ├── reminder.py
│   └── user.py
├── services/
│   ├── __init__.py
│   ├── plan_service.py
│   ├── reminder_service.py
│   └── notification_service.py
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── plans.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── validation.py
│   └── schemas/
│       ├── __init__.py
│       └── plan_schemas.py
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   └── security.py
└── main.py

tests/
├── contract/
│   └── test_plans_api_contract.py
├── integration/
│   ├── test_plan_crud.py
│   ├── test_plan_reminders.py
│   └── test_plan_management.py
└── unit/
    ├── test_plan_service.py
    ├── test_reminder_service.py
    └── test_validators.py
```

**Structure Decision**: 选择单体 API 架构（Single project），理由如下：
1. 健身计划管理是独立功能模块，但作为运动管家 API 的一部分
2. 采用分层架构：API 层（routes + schemas）→ 业务逻辑层（services）→ 数据访问层（models）
3. 核心基础设施（config, database, security）统一放在 core/ 目录
4. 测试按类型分层：契约测试（API 接口）、集成测试（业务流程）、单元测试（服务逻辑）

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

无需填写 - 所有 Constitution 原则均已满足，无复杂性豁免。
