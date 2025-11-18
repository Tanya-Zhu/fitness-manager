# Quickstart: 健身计划管理开发指南

**Feature**: 健身计划管理
**Date**: 2025-11-10
**Audience**: 开发者

## 概述

本指南帮助开发者快速搭建健身计划管理功能的开发环境，并了解核心工作流程。

---

## 前置要求

### 必需工具

- **Python**: 3.11 或更高版本
- **PostgreSQL**: 15 或更高版本
- **Redis**: 7 或更高版本
- **Docker & Docker Compose**: 用于本地服务编排
- **Git**: 版本控制

### 可选工具

- **Poetry** 或 **pip-tools**: Python 依赖管理
- **Postman** 或 **HTTPie**: API 测试
- **pgAdmin** 或 **DBeaver**: 数据库管理

---

## 快速启动

### 1. 环境搭建

```bash
# 克隆仓库并切换到功能分支
git clone <repository-url>
cd my-project
git checkout 001-fitness-plan-management

# 创建 Python 虚拟环境
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖（pytest, black, etc.）

# 复制环境变量模板
cp .env.example .env
# 编辑 .env 文件，配置数据库连接、JWT 密钥等
```

### 2. 启动基础服务（Docker Compose）

```bash
# 启动 PostgreSQL + Redis
docker-compose up -d db redis

# 验证服务运行
docker-compose ps
```

**docker-compose.yml** (示例):
```yaml
version: '3.8'
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: fitness_user
      POSTGRES_PASSWORD: fitness_pass
      POSTGRES_DB: fitness_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 3. 数据库迁移

```bash
# 初始化 Alembic（首次）
alembic init alembic

# 生成初始迁移脚本
alembic revision --autogenerate -m "Initial fitness plan schema"

# 应用迁移
alembic upgrade head

# 验证表创建
psql -h localhost -U fitness_user -d fitness_db -c "\dt"
```

### 4. 运行开发服务器

```bash
# 启动 FastAPI 应用（带热重载）
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 访问 API 文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## 项目结构导览

```
my-project/
├── src/                        # 应用代码
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── fitness_plan.py     # 健身计划模型
│   │   ├── exercise.py         # 锻炼项目模型
│   │   └── reminder.py         # 提醒模型
│   ├── services/               # 业务逻辑层
│   │   ├── plan_service.py     # 计划管理服务
│   │   ├── reminder_service.py # 提醒调度服务
│   │   └── notification_service.py  # 通知发送服务
│   ├── api/                    # API 层
│   │   ├── routes/             # 路由定义
│   │   │   └── plans.py        # 计划相关端点
│   │   ├── middleware/         # 中间件
│   │   │   ├── auth.py         # JWT 认证
│   │   │   └── validation.py   # 请求验证
│   │   └── schemas/            # Pydantic 模型
│   │       └── plan_schemas.py # 请求/响应模型
│   ├── core/                   # 核心配置
│   │   ├── config.py           # 环境变量配置
│   │   ├── database.py         # 数据库连接
│   │   └── security.py         # JWT + 密码哈希
│   └── main.py                 # FastAPI 应用入口
├── tests/                      # 测试代码
│   ├── contract/               # API 契约测试
│   ├── integration/            # 集成测试
│   └── unit/                   # 单元测试
├── alembic/                    # 数据库迁移
├── specs/                      # 功能规范文档
├── .env.example                # 环境变量模板
├── requirements.txt            # 生产依赖
└── docker-compose.yml          # 本地服务编排
```

---

## 核心开发流程

### Step 1: 创建数据模型（SQLAlchemy）

**文件**: `src/models/fitness_plan.py`

```python
from sqlalchemy import Column, String, Enum, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from src.core.database import Base

class FitnessPlan(Base):
    __tablename__ = "fitness_plan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum('active', 'paused', name='plan_status'), nullable=False, default='active')
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(TIMESTAMP, nullable=True)

    # 关系
    exercises = relationship("Exercise", back_populates="plan", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="plan", cascade="all, delete-orphan")
```

### Step 2: 定义 API Schemas（Pydantic）

**文件**: `src/api/schemas/plan_schemas.py`

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ExerciseCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    duration_minutes: Optional[int] = Field(None, gt=0)
    repetitions: Optional[int] = Field(None, gt=0)
    intensity: str = Field(default="medium", pattern="^(low|medium|high)$")
    order_index: int = Field(default=0, ge=0)

    @validator('duration_minutes', 'repetitions')
    def check_duration_or_reps(cls, v, values):
        # 至少填写一个
        if 'duration_minutes' in values and not v and not values.get('duration_minutes'):
            raise ValueError('duration_minutes 或 repetitions 必须至少填写一个')
        return v

class FitnessPlanCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    exercises: List[ExerciseCreate] = Field(..., min_items=1)

class FitnessPlanResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy 2.0
```

### Step 3: 实现业务逻辑（Service 层）

**文件**: `src/services/plan_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from typing import List

from src.models.fitness_plan import FitnessPlan
from src.api.schemas.plan_schemas import FitnessPlanCreate

class PlanService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_plan(self, user_id: UUID, plan_data: FitnessPlanCreate) -> FitnessPlan:
        """创建健身计划"""
        plan = FitnessPlan(
            user_id=user_id,
            name=plan_data.name,
            description=plan_data.description
        )
        self.db.add(plan)

        # 添加锻炼项目
        for exercise_data in plan_data.exercises:
            exercise = Exercise(**exercise_data.dict(), plan_id=plan.id)
            self.db.add(exercise)

        await self.db.commit()
        await self.db.refresh(plan)
        return plan

    async def get_user_plans(self, user_id: UUID, status: Optional[str] = None) -> List[FitnessPlan]:
        """获取用户的计划列表"""
        query = select(FitnessPlan).where(
            FitnessPlan.user_id == user_id,
            FitnessPlan.deleted_at.is_(None)
        )
        if status:
            query = query.where(FitnessPlan.status == status)

        result = await self.db.execute(query)
        return result.scalars().all()
```

### Step 4: 创建 API 端点（FastAPI）

**文件**: `src/api/routes/plans.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.core.database import get_db
from src.core.security import get_current_user
from src.services.plan_service import PlanService
from src.api.schemas.plan_schemas import FitnessPlanCreate, FitnessPlanResponse

router = APIRouter(prefix="/api/v1/plans", tags=["plans"])

@router.post("/", response_model=FitnessPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_fitness_plan(
    plan_data: FitnessPlanCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建新的健身计划"""
    service = PlanService(db)
    plan = await service.create_plan(current_user['user_id'], plan_data)
    return plan

@router.get("/", response_model=List[FitnessPlanResponse])
async def list_fitness_plans(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的健身计划列表"""
    service = PlanService(db)
    plans = await service.get_user_plans(current_user['user_id'], status)
    return plans
```

### Step 5: 编写测试（TDD）

**文件**: `tests/integration/test_plan_crud.py`

```python
import pytest
from httpx import AsyncClient
from src.main import app

@pytest.mark.asyncio
async def test_create_fitness_plan(auth_client: AsyncClient):
    """测试创建健身计划"""
    plan_data = {
        "name": "减脂训练",
        "description": "每周3次有氧",
        "exercises": [
            {"name": "跑步", "duration_minutes": 30, "intensity": "medium"},
            {"name": "俯卧撑", "repetitions": 20, "intensity": "high"}
        ]
    }

    response = await auth_client.post("/api/v1/plans", json=plan_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "减脂训练"
    assert len(data["exercises"]) == 2

@pytest.mark.asyncio
async def test_create_plan_without_name_fails(auth_client: AsyncClient):
    """测试没有名称的计划创建失败"""
    plan_data = {
        "exercises": [{"name": "跑步", "duration_minutes": 30}]
    }

    response = await auth_client.post("/api/v1/plans", json=plan_data)

    assert response.status_code == 400
    assert "name" in response.json()["detail"].lower()
```

---

## 关键配置

### 环境变量 (.env)

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://fitness_user:fitness_pass@localhost:5432/fitness_db

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# JWT 配置
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=RS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# 应用配置
APP_ENV=development
LOG_LEVEL=INFO
```

### 数据库连接 (src/core/database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from src.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True if settings.APP_ENV == "development" else False,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

---

## 测试运行

### 运行所有测试

```bash
# 完整测试套件
pytest

# 带覆盖率报告
pytest --cov=src --cov-report=html
```

### 按层级运行

```bash
# 单元测试（快速）
pytest tests/unit -v

# 集成测试（需要数据库）
pytest tests/integration -v

# 契约测试（API 规范验证）
pytest tests/contract -v
```

### 并行测试（加速）

```bash
# 使用 pytest-xdist
pytest -n auto
```

---

## 常见任务

### 添加新的 API 端点

1. 在 `src/api/routes/plans.py` 定义路由
2. 在 `src/api/schemas/` 定义请求/响应模型
3. 在 `src/services/` 实现业务逻辑
4. 编写测试 `tests/integration/test_*.py`
5. 更新 OpenAPI 文档（FastAPI 自动生成）

### 数据库模型变更

1. 修改 `src/models/*.py` 中的模型定义
2. 生成迁移脚本: `alembic revision --autogenerate -m "描述"`
3. 检查生成的迁移脚本 `alembic/versions/*.py`
4. 应用迁移: `alembic upgrade head`
5. 更新 `specs/001-fitness-plan-management/data-model.md`

### 调试技巧

**启用 SQL 日志**:
```python
# src/core/database.py
engine = create_async_engine(DATABASE_URL, echo=True)
```

**使用 pdb 断点**:
```python
import pdb; pdb.set_trace()
```

**FastAPI 响应验证**:
```python
# 访问 /docs 交互式测试 API
# 自动显示请求/响应模型和验证错误
```

---

## 提醒调度设置

### APScheduler 配置

**文件**: `src/services/reminder_service.py`

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.triggers.cron import CronTrigger

scheduler = AsyncIOScheduler(
    jobstores={'default': RedisJobStore(host='localhost', port=6379)}
)

async def schedule_reminder(plan_id: UUID, reminder_time: str, days_of_week: List[int]):
    """添加提醒任务"""
    job_id = f"reminder_{plan_id}"

    # 解析 reminder_time (如 "08:00:00")
    hour, minute, second = reminder_time.split(":")

    # 创建 Cron 触发器（周一三五 8:00）
    trigger = CronTrigger(
        day_of_week=','.join(map(str, days_of_week)),
        hour=int(hour),
        minute=int(minute),
        second=int(second)
    )

    scheduler.add_job(
        send_notification,  # 回调函数
        trigger=trigger,
        args=[plan_id],
        id=job_id,
        replace_existing=True
    )
```

### 启动调度器

**文件**: `src/main.py`

```python
from fastapi import FastAPI
from src.services.reminder_service import scheduler

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
```

---

## 下一步

1. **实现 MVP**: 先完成 P1 用户故事（创建计划 + 提醒）
2. **集成认证**: 实现 JWT 认证中间件
3. **通知集成**: 对接 Firebase Cloud Messaging
4. **性能优化**: 添加 Redis 缓存、数据库查询优化
5. **部署准备**: 编写 Dockerfile、配置 CI/CD

---

## 参考资源

- **FastAPI 文档**: https://fastapi.tiangolo.com
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **APScheduler**: https://apscheduler.readthedocs.io
- **Pydantic**: https://docs.pydantic.dev
- **项目规范**: `specs/001-fitness-plan-management/spec.md`
- **API 契约**: `specs/001-fitness-plan-management/contracts/fitness-plans-api.yaml`

---

**准备开发？运行 `pytest` 确认环境配置正确，然后开始编写第一个测试！**
