# 运动管家 - 使用指南

## 快速开始

### 1. 环境准备

#### 前置要求
- Python 3.11+
- Docker 和 Docker Compose（用于运行PostgreSQL和Redis）

#### 安装步骤

```bash
# 1. 创建Python虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者在Windows上: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 3. 启动数据库和Redis
docker-compose up -d

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的配置（数据库URL、JWT密钥等）

# 5. 运行数据库迁移
alembic upgrade head

# 6. 启动应用
python src/main.py
```

应用将在 http://localhost:8000 启动

### 2. API文档

应用启动后，访问以下地址查看交互式API文档：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 认证流程

### 2.1 注册新用户

**端点**: `POST /api/v1/auth/register`

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "your_password_123",
  "full_name": "张三"
}
```

**响应示例** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "张三",
  "created_at": "2025-11-10T08:00:00"
}
```

**使用curl**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password_123",
    "full_name": "张三"
  }'
```

### 2.2 用户登录

**端点**: `POST /api/v1/auth/login`

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "your_password_123"
}
```

**响应示例** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**使用curl**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password_123"
  }'
```

**重要**: 保存返回的 `access_token`，后续所有请求都需要使用它。

### 2.3 获取当前用户信息

**端点**: `GET /api/v1/auth/me`

**请求头**:
```
Authorization: Bearer {your_access_token}
```

**使用curl**:
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 健身计划管理

所有以下端点都需要在请求头中包含JWT token：
```
Authorization: Bearer {your_access_token}
```

### 3.1 创建健身计划

**端点**: `POST /api/v1/plans`

**请求体**:
```json
{
  "name": "减脂训练",
  "description": "每周3次有氧运动",
  "exercises": [
    {
      "name": "跑步",
      "duration_minutes": 30,
      "intensity": "medium",
      "order_index": 0
    },
    {
      "name": "俯卧撑",
      "repetitions": 20,
      "intensity": "high",
      "order_index": 1
    }
  ]
}
```

**使用curl**:
```bash
curl -X POST http://localhost:8000/api/v1/plans \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "减脂训练",
    "description": "每周3次有氧运动",
    "exercises": [
      {
        "name": "跑步",
        "duration_minutes": 30,
        "intensity": "medium"
      },
      {
        "name": "俯卧撑",
        "repetitions": 20,
        "intensity": "high"
      }
    ]
  }'
```

### 3.2 查看所有健身计划

**端点**: `GET /api/v1/plans`

**查询参数**:
- `page`: 页码（默认: 1）
- `page_size`: 每页条数（默认: 20）
- `status`: 筛选状态 (active/paused)

**使用curl**:
```bash
curl -X GET "http://localhost:8000/api/v1/plans?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3.3 查看计划详情

**端点**: `GET /api/v1/plans/{plan_id}`

**使用curl**:
```bash
curl -X GET http://localhost:8000/api/v1/plans/{plan_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3.4 更新健身计划

**端点**: `PUT /api/v1/plans/{plan_id}`

**请求体** (支持部分更新):
```json
{
  "name": "新名称",
  "description": "更新后的描述"
}
```

**使用curl**:
```bash
curl -X PUT http://localhost:8000/api/v1/plans/{plan_id} \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新名称",
    "description": "更新后的描述"
  }'
```

### 3.5 删除健身计划

**端点**: `DELETE /api/v1/plans/{plan_id}`

**使用curl**:
```bash
curl -X DELETE http://localhost:8000/api/v1/plans/{plan_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 锻炼项目管理

### 4.1 添加锻炼项目

**端点**: `POST /api/v1/plans/{plan_id}/exercises`

**请求体**:
```json
{
  "name": "深蹲",
  "repetitions": 15,
  "intensity": "medium"
}
```

**使用curl**:
```bash
curl -X POST http://localhost:8000/api/v1/plans/{plan_id}/exercises \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "深蹲",
    "repetitions": 15,
    "intensity": "medium"
  }'
```

### 4.2 更新锻炼项目

**端点**: `PUT /api/v1/plans/{plan_id}/exercises/{exercise_id}`

**请求体**:
```json
{
  "name": "快速跑步",
  "duration_minutes": 45,
  "intensity": "high"
}
```

### 4.3 删除锻炼项目

**端点**: `DELETE /api/v1/plans/{plan_id}/exercises/{exercise_id}`

**注意**: 不能删除计划中的最后一个锻炼项目。

---

## 提醒功能

### 5.1 添加提醒

**端点**: `POST /api/v1/plans/{plan_id}/reminders`

**请求体**:
```json
{
  "reminder_time": "07:30:00",
  "frequency": "daily",
  "days_of_week": [1, 2, 3, 4, 5],
  "is_enabled": true
}
```

- `reminder_time`: 24小时制时间 (HH:MM:SS)
- `frequency`: "daily"(每天), "weekly"(每周), "custom"(自定义)
- `days_of_week`: 1-7 表示周一到周日

**使用curl**:
```bash
curl -X POST http://localhost:8000/api/v1/plans/{plan_id}/reminders \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reminder_time": "07:30:00",
    "frequency": "daily",
    "days_of_week": [1, 2, 3, 4, 5],
    "is_enabled": true
  }'
```

### 5.2 更新提醒

**端点**: `PUT /api/v1/plans/{plan_id}/reminders/{reminder_id}`

### 5.3 删除提醒

**端点**: `DELETE /api/v1/plans/{plan_id}/reminders/{reminder_id}`

---

## 使用Postman或其他API客户端

### 设置认证

1. 登录获取token
2. 在Postman中设置Authorization:
   - Type: Bearer Token
   - Token: 粘贴你的access_token

### 在Swagger UI中测试

1. 访问 http://localhost:8000/docs
2. 点击右上角的 "Authorize" 按钮
3. 输入: `Bearer YOUR_TOKEN`
4. 点击 "Authorize"
5. 现在可以直接在Swagger UI中测试所有端点

---

## 常见问题

### Q: Token过期怎么办？
A: Access token默认15分钟后过期。过期后需要重新登录获取新token。

### Q: 忘记密码怎么办？
A: 当前版本未实现密码重置功能。需要联系管理员或重新注册。

### Q: 如何查看所有API端点？
A: 访问 http://localhost:8000/docs 查看完整的API文档。

### Q: 数据库连接失败？
A: 确保已运行 `docker-compose up -d` 启动PostgreSQL和Redis服务。

### Q: 如何停止服务？
A:
- 停止应用: Ctrl+C
- 停止数据库: `docker-compose down`

---

## 开发测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定类型的测试
pytest -m unit          # 单元测试
pytest -m integration   # 集成测试
pytest -m contract      # 契约测试

# 查看测试覆盖率
pytest --cov=src --cov-report=html
```

### 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

---

## 技术支持

如有问题或建议，请联系开发团队。
