# Data Model: 健身计划管理

**Feature**: 健身计划管理
**Date**: 2025-11-10
**Phase**: Phase 1 - Design

## Overview

本文档定义健身计划管理功能的数据模型，包括实体、字段、关系和验证规则。模型设计遵循规范中定义的功能需求和 Constitution 的数据准确性原则。

---

## Entity Relationship Diagram

```
┌──────────────┐           ┌──────────────────┐
│    User      │           │  FitnessPlan     │
│──────────────│           │──────────────────│
│ id (PK)      │───────────│ id (PK)          │
│ email        │    1:N    │ user_id (FK)     │
│ password_hash│           │ name             │
│ created_at   │           │ description      │
└──────────────┘           │ status           │
                           │ created_at       │
                           │ updated_at       │
                           │ deleted_at       │
                           └──────────────────┘
                                   │
                                   │ 1:N
                                   ▼
                           ┌──────────────────┐
                           │    Exercise      │
                           │──────────────────│
                           │ id (PK)          │
                           │ plan_id (FK)     │
                           │ name             │
                           │ duration_minutes │
                           │ repetitions      │
                           │ intensity        │
                           │ order_index      │
                           │ created_at       │
                           └──────────────────┘

┌──────────────────┐       ┌──────────────────┐
│  FitnessPlan     │       │    Reminder      │
│──────────────────│       │──────────────────│
│ id (PK)          │───────│ id (PK)          │
│ ...              │  1:N  │ plan_id (FK)     │
└──────────────────┘       │ reminder_time    │
                           │ frequency        │
                           │ days_of_week     │
                           │ is_enabled       │
                           │ created_at       │
                           │ updated_at       │
                           └──────────────────┘
```

---

## Entities

### 1. User（用户）

**Purpose**: 表示使用运动管家的注册用户

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | 用户唯一标识符 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 用户邮箱（用于登录） |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希值（bcrypt） |
| full_name | VARCHAR(100) | NULLABLE | 用户全名 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 最后更新时间 |

**Indexes**:
- PRIMARY KEY (id)
- UNIQUE INDEX (email)

**Validation Rules**:
- email: 必须符合邮箱格式（RFC 5322）
- password_hash: 最小长度 60 字符（bcrypt 输出）
- full_name: 最大 100 字符

**Relationships**:
- 一个用户可以拥有多个健身计划（1:N → FitnessPlan）

---

### 2. FitnessPlan（健身计划）

**Purpose**: 表示用户创建的健身计划

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | 计划唯一标识符 |
| user_id | UUID | FK, NOT NULL, INDEX | 所属用户ID（外键 → User.id） |
| name | VARCHAR(50) | NOT NULL | 计划名称 |
| description | TEXT | NULLABLE | 计划目标描述 |
| status | ENUM | NOT NULL, DEFAULT 'active' | 计划状态：'active', 'paused' |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 最后更新时间 |
| deleted_at | TIMESTAMP | NULLABLE | 软删除时间戳 |

**Indexes**:
- PRIMARY KEY (id)
- INDEX (user_id, status, deleted_at) - 复合索引，优化用户计划列表查询
- INDEX (updated_at) - 优化按更新时间排序

**Validation Rules** (来自 FR-014, FR-015):
- name: 非空，长度 1-50 字符
- status: 只能是 'active' 或 'paused'
- 每个计划必须至少包含一个锻炼项目（通过应用层验证）

**Relationships**:
- 属于一个用户（N:1 → User）
- 包含多个锻炼项目（1:N → Exercise）
- 包含多个提醒设置（1:N → Reminder）

**Business Rules**:
- 软删除：deleted_at 不为 NULL 时视为已删除
- 级联删除：删除计划时同时删除关联的 Exercise 和 Reminder

---

### 3. Exercise（锻炼项目）

**Purpose**: 表示健身计划中的具体锻炼内容

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | 锻炼项目唯一标识符 |
| plan_id | UUID | FK, NOT NULL, INDEX | 所属计划ID（外键 → FitnessPlan.id） |
| name | VARCHAR(100) | NOT NULL | 锻炼项目名称（如"跑步"） |
| duration_minutes | INTEGER | NULLABLE, CHECK (> 0) | 锻炼时长（分钟），与 repetitions 互斥 |
| repetitions | INTEGER | NULLABLE, CHECK (> 0) | 锻炼次数（如"20个俯卧撑"） |
| intensity | ENUM | NOT NULL, DEFAULT 'medium' | 强度级别：'low', 'medium', 'high' |
| order_index | INTEGER | NOT NULL, DEFAULT 0 | 排序顺序（0-based） |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |

**Indexes**:
- PRIMARY KEY (id)
- INDEX (plan_id, order_index) - 复合索引，优化按顺序查询

**Validation Rules** (来自 FR-002):
- name: 非空，长度 1-100 字符
- duration_minutes 或 repetitions 必须至少填写一个（通过应用层验证）
- duration_minutes: 如果填写，必须 > 0
- repetitions: 如果填写，必须 > 0
- intensity: 只能是 'low', 'medium', 'high'
- order_index: 必须 >= 0

**Relationships**:
- 属于一个健身计划（N:1 → FitnessPlan）

**Business Rules**:
- 级联删除：删除计划时自动删除所有锻炼项目
- 排序：同一计划内的项目按 order_index 升序排列

---

### 4. Reminder（提醒设置）

**Purpose**: 表示健身计划的提醒配置

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, NOT NULL | 提醒唯一标识符 |
| plan_id | UUID | FK, NOT NULL, INDEX | 所属计划ID（外键 → FitnessPlan.id） |
| reminder_time | TIME | NOT NULL | 提醒时间（如 08:00:00） |
| frequency | ENUM | NOT NULL, DEFAULT 'weekly' | 提醒频率：'daily', 'weekly', 'custom' |
| days_of_week | JSONB | NULLABLE | 每周提醒日期（如 [1,3,5] 表示周一三五）|
| is_enabled | BOOLEAN | NOT NULL, DEFAULT true | 是否启用提醒 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 最后更新时间 |

**Indexes**:
- PRIMARY KEY (id)
- INDEX (plan_id, is_enabled) - 复合索引，优化查询启用的提醒

**Validation Rules** (来自 FR-008, FR-009, FR-011):
- reminder_time: 必须是有效的时间格式（HH:MM:SS）
- frequency: 只能是 'daily', 'weekly', 'custom'
- days_of_week:
  - 仅当 frequency = 'weekly' 或 'custom' 时需要
  - 数组元素必须是 1-7（1=周一, 7=周日）
- is_enabled: 控制是否发送提醒

**Relationships**:
- 属于一个健身计划（N:1 → FitnessPlan）

**Business Rules**:
- 级联删除：删除计划时自动删除所有提醒设置
- 暂停计划：计划状态为 'paused' 时，忽略所有提醒（即使 is_enabled=true）
- APScheduler Job ID 格式：`reminder_{plan_id}_{reminder_id}`

---

## State Transitions

### FitnessPlan.status

```
[创建] → active (默认状态)
    ↓
active ←→ paused (用户可随时切换)
    ↓
active/paused → (软删除: deleted_at 设置时间戳)
```

**Transitions**:
- **创建**: 新建计划时状态默认为 'active'
- **暂停**: 用户调用 PATCH /api/v1/plans/{id}/pause → status = 'paused'
- **恢复**: 用户调用 PATCH /api/v1/plans/{id}/resume → status = 'active'
- **删除**: 用户调用 DELETE /api/v1/plans/{id} → deleted_at = NOW()

**Side Effects**:
- status = 'paused': 所有关联的提醒任务停止触发（但 Reminder 记录保留）
- status = 'active': 重新启用提醒任务（仅当 Reminder.is_enabled=true）
- deleted_at != NULL: 从用户计划列表中隐藏，相关提醒任务从 APScheduler 移除

---

## Validation Summary

### Database Constraints

| Entity | Field | Constraint | Error Message |
|--------|-------|------------|---------------|
| FitnessPlan | name | NOT NULL | "计划名称不能为空" |
| FitnessPlan | name | LENGTH(1-50) | "计划名称长度必须在1-50字符之间" |
| Exercise | plan_id | FOREIGN KEY | "关联的计划不存在" |
| Exercise | duration_minutes | > 0 | "锻炼时长必须大于0" |
| Exercise | repetitions | > 0 | "锻炼次数必须大于0" |
| Reminder | plan_id | FOREIGN KEY | "关联的计划不存在" |
| Reminder | days_of_week | ARRAY[1-7] | "星期必须在1-7之间" |

### Application-Level Validation

| Rule | Source | Validation Logic |
|------|--------|------------------|
| 计划至少一个锻炼项目 | FR-015 | 创建/更新计划时检查 Exercise 数量 >= 1 |
| duration_minutes / repetitions 互斥 | FR-002 | 至少填写一个，不能同时为 NULL |
| days_of_week 与 frequency 一致 | FR-003 | frequency='daily' 时 days_of_week 应为 NULL 或 [1-7] |
| 用户只能访问自己的计划 | Constitution V | 所有查询必须过滤 `WHERE user_id = current_user.id` |

---

## Query Patterns

### Common Queries

**1. 用户计划列表（带分页）**
```sql
SELECT * FROM fitness_plan
WHERE user_id = :user_id
  AND deleted_at IS NULL
ORDER BY updated_at DESC
LIMIT :page_size OFFSET :offset;
```
**Index Used**: (user_id, status, deleted_at)

**2. 计划详情（包含锻炼项目）**
```sql
SELECT p.*, e.*
FROM fitness_plan p
LEFT JOIN exercise e ON p.id = e.plan_id
WHERE p.id = :plan_id
  AND p.user_id = :user_id
  AND p.deleted_at IS NULL
ORDER BY e.order_index;
```
**Index Used**: (plan_id, order_index) for Exercise

**3. 活动计划的提醒列表**
```sql
SELECT r.*
FROM reminder r
JOIN fitness_plan p ON r.plan_id = p.id
WHERE p.user_id = :user_id
  AND p.status = 'active'
  AND p.deleted_at IS NULL
  AND r.is_enabled = true;
```
**Index Used**: (plan_id, is_enabled) for Reminder

---

## Migration Strategy

### Initial Schema (Alembic Migration)

```python
# alembic/versions/001_initial_fitness_plan_schema.py

def upgrade():
    # 创建 ENUM 类型
    op.execute("CREATE TYPE plan_status AS ENUM ('active', 'paused')")
    op.execute("CREATE TYPE exercise_intensity AS ENUM ('low', 'medium', 'high')")
    op.execute("CREATE TYPE reminder_frequency AS ENUM ('daily', 'weekly', 'custom')")

    # 创建 fitness_plan 表
    op.create_table(
        'fitness_plan',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('active', 'paused', name='plan_status'), nullable=False, default='active'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.func.now()),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    )

    # 创建索引
    op.create_index('idx_fitness_plan_user_status', 'fitness_plan', ['user_id', 'status', 'deleted_at'])

    # 创建 exercise 表 (类似逻辑)
    # 创建 reminder 表 (类似逻辑)
```

---

## Data Model Checklist

- [x] 所有实体映射到规范的 Key Entities
- [x] 字段类型和约束明确定义
- [x] 外键关系和索引优化
- [x] 验证规则来源可追溯（FR-001 ~ FR-017）
- [x] 状态转换逻辑清晰
- [x] 查询模式考虑性能优化
- [x] 符合 Constitution 原则（数据准确性、模块化）

---

## Next Steps

- **Phase 1 继续**: 生成 API contracts（基于此数据模型）
- **实现阶段**: 使用 SQLAlchemy 2.0 模型定义这些实体
- **测试**: 编写数据模型的单元测试（验证规则、关系）
