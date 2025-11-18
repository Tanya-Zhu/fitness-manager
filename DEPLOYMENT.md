# 运动管家 - 部署指南

本文档提供将应用部署到 anker-launch 平台的完整步骤。

## 目录

- [准备工作](#准备工作)
- [配置环境变量](#配置环境变量)
- [部署步骤](#部署步骤)
- [部署后验证](#部署后验证)
- [常见问题](#常见问题)

## 准备工作

### 1. 确保所有文件已提交到 Git

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. 检查必需文件

确保以下文件存在于项目根目录：

- ✅ `requirements.txt` - Python 依赖列表
- ✅ `runtime.txt` - Python 版本声明
- ✅ `Procfile` - 应用启动配置
- ✅ `.env.production` - 生产环境变量模板
- ✅ `alembic.ini` - 数据库迁移配置
- ✅ `alembic/versions/` - 数据库迁移脚本

## 配置环境变量

### 1. 在 anker-launch 平台控制台配置

登录 https://go.anker-launch.com/dashboard，进入您的项目设置页面，配置以下环境变量：

#### 必需配置项

```bash
# 应用环境
APP_ENV=production
LOG_LEVEL=INFO

# 数据库连接 (从平台控制台获取)
DATABASE_URL=postgresql+asyncpg://username:password@hostname:5432/database_name

# Redis 连接 (如果平台提供)
# 如果没有 Redis，可以使用内存模式: REDIS_URL=memory://
REDIS_URL=redis://hostname:6379/0

# JWT 密钥 (重要：必须更改为安全的随机密钥)
# 生成命令: openssl rand -hex 32
JWT_SECRET_KEY=your-secure-random-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# API 配置
API_V1_PREFIX=/api/v1
CORS_ORIGINS=https://your-domain.com,https://go.anker-launch.com

# 分页配置
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

#### 可选配置项

```bash
# 推送通知 (如需启用)
# FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
# PUSH_NOTIFICATION_ENABLED=false
```

### 2. 生成安全的 JWT 密钥

在本地终端运行以下命令生成安全密钥：

```bash
openssl rand -hex 32
```

将生成的密钥复制到平台的 `JWT_SECRET_KEY` 环境变量中。

### 3. 获取数据库连接信息

1. 在 anker-launch 平台控制台中找到数据库服务
2. 复制数据库连接字符串
3. 确保格式为: `postgresql+asyncpg://username:password@hostname:5432/database_name`
4. 将其设置为 `DATABASE_URL` 环境变量

## 部署步骤

### 方式 1: 通过 Git 部署（推荐）

1. **连接 Git 仓库**

   在 anker-launch 控制台中：
   - 选择 "部署方式" > "Git"
   - 连接您的 GitHub/GitLab 仓库
   - 选择要部署的分支（通常是 `main` 或 `master`）

2. **配置构建设置**

   平台应该能自动识别 Python 应用，如果需要手动配置：

   - 构建命令: `pip install -r requirements.txt`
   - 启动命令: 系统会自动读取 `Procfile`

3. **触发部署**

   - 点击 "部署" 按钮
   - 等待构建完成（通常需要 2-5 分钟）

### 方式 2: 通过命令行工具部署

如果 anker-launch 提供 CLI 工具：

```bash
# 安装 CLI（如果需要）
npm install -g anker-launch-cli

# 登录
anker-launch login

# 部署
anker-launch deploy
```

### 方式 3: 手动上传

1. 打包项目：

```bash
# 创建部署包（排除不必要的文件）
tar -czf deploy.tar.gz \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='venv' \
  --exclude='node_modules' \
  .
```

2. 在控制台上传 `deploy.tar.gz`

## 部署后验证

### 1. 检查应用状态

```bash
# 访问健康检查端点
curl https://your-app-url.anker-launch.com/health
```

预期响应：

```json
{
  "status": "healthy",
  "timestamp": "2024-11-17T10:00:00Z"
}
```

### 2. 验证 API 文档

访问: `https://your-app-url.anker-launch.com/api/docs`

应该能看到 Swagger UI 文档页面。

### 3. 测试静态文件

访问: `https://your-app-url.anker-launch.com/`

应该能看到前端页面。

### 4. 检查数据库连接

```bash
# 测试注册接口
curl -X POST https://your-app-url.anker-launch.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 5. 查看日志

在 anker-launch 控制台中查看应用日志，确认：

- ✅ 应用成功启动
- ✅ 数据库连接成功
- ✅ 数据库迁移完成
- ✅ APScheduler 启动（如果使用 Redis）

## 常见问题

### Q1: 数据库迁移失败

**症状**: 日志显示 "relation does not exist" 错误

**解决方案**:

1. 确认 `DATABASE_URL` 配置正确
2. 检查 Procfile 中的 `release` 命令是否执行
3. 手动运行迁移:

```bash
# 在平台控制台的终端中运行
alembic upgrade head
```

### Q2: 静态文件无法访问

**症状**: 访问根路径 `/` 返回 404

**解决方案**:

1. 确认 `static/` 目录存在且包含 HTML 文件
2. 检查 `src/main.py` 中的静态文件挂载配置
3. 确保静态文件已提交到 Git

### Q3: CORS 错误

**症状**: 前端请求 API 时出现跨域错误

**解决方案**:

更新 `CORS_ORIGINS` 环境变量，添加您的前端域名：

```bash
CORS_ORIGINS=https://your-frontend-domain.com,https://go.anker-launch.com
```

### Q4: 应用启动后立即崩溃

**解决方案**:

1. 检查所有必需的环境变量是否已配置
2. 查看启动日志，找出具体错误
3. 常见原因：
   - `JWT_SECRET_KEY` 未设置
   - `DATABASE_URL` 格式错误
   - Python 版本不匹配

### Q5: Redis 连接失败

**症状**: 日志显示 Redis 连接错误，但应用仍在运行

**说明**: 这是正常的，应用会自动降级到内存模式

**解决方案**（如果需要 Redis）:

1. 在平台控制台中启用 Redis 服务
2. 更新 `REDIS_URL` 环境变量
3. 重启应用

## 性能优化建议

### 1. 启用生产模式

确保 `APP_ENV=production`，这将：
- 禁用自动重载
- 优化日志输出
- 启用生产级错误处理

### 2. 配置 Worker 数量

在 Procfile 中调整 worker 数量：

```
web: uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4
```

建议：`workers = (2 × CPU 核心数) + 1`

### 3. 使用 Redis

如果平台提供 Redis，强烈建议启用以提升：
- 定时任务可靠性
- 会话管理性能

### 4. 数据库连接池

当前配置已优化数据库连接池，如需调整可在 `src/core/database.py` 中修改：

```python
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 最大溢出连接数
)
```

## 回滚部署

如果需要回滚到之前的版本：

1. **Git 部署**: 在控制台选择之前的 commit
2. **手动部署**: 上传之前的部署包
3. **快速回滚**: 使用平台的回滚功能（如果支持）

## 监控和维护

### 健康检查

应用提供健康检查端点: `/health`

配置监控服务定期检查此端点。

### 日志监控

定期检查以下日志：
- 应用错误日志
- 数据库连接日志
- API 请求日志

### 数据库备份

建议：
- 启用平台的自动备份功能
- 定期手动导出数据库快照

## 获取帮助

如果遇到问题：

1. 查看平台文档: https://go.anker-launch.com/docs
2. 查看应用日志
3. 检查本文档的常见问题部分
4. 联系平台技术支持

## 安全检查清单

部署前请确认：

- [ ] `JWT_SECRET_KEY` 已更改为安全的随机密钥
- [ ] 数据库密码足够强
- [ ] `CORS_ORIGINS` 仅包含信任的域名
- [ ] `APP_ENV` 设置为 `production`
- [ ] 敏感信息未硬编码在代码中
- [ ] `.env` 文件未提交到 Git
- [ ] 所有依赖版本已固定在 `requirements.txt`

## 总结

完成以上步骤后，您的应用应该已成功部署到 anker-launch 平台。如有任何问题，请参考常见问题部分或查看平台日志进行排查。

祝您部署顺利！ 🚀
