# 快速部署指南

5 分钟快速部署到 anker-launch 平台

## 前置要求

- ✅ anker-launch 平台账号
- ✅ Git 仓库（GitHub/GitLab）
- ✅ 项目代码已推送到远程仓库

## 部署步骤

### 1. 生成安全密钥 (1分钟)

```bash
# 在本地终端运行
openssl rand -hex 32
```

复制生成的密钥，稍后使用。

### 2. 登录 anker-launch 平台 (1分钟)

访问: https://go.anker-launch.com/dashboard

### 3. 创建新应用 (1分钟)

1. 点击 "新建应用" 或 "Create New App"
2. 选择 "从 Git 仓库部署"
3. 连接你的 GitHub/GitLab 账号
4. 选择本项目仓库
5. 选择分支（通常是 `main`）

### 4. 配置数据库 (1分钟)

1. 在应用设置中找到 "数据库服务"
2. 创建 PostgreSQL 数据库
3. 复制数据库连接字符串（格式如: `postgresql://...`）

### 5. 设置环境变量 (1分钟)

在应用的环境变量设置中添加：

```bash
# 必需配置
APP_ENV=production
DATABASE_URL=<从步骤4复制的数据库连接字符串，记得改为 postgresql+asyncpg://>
JWT_SECRET_KEY=<从步骤1生成的密钥>

# 可选配置（使用默认值）
REDIS_URL=memory://
LOG_LEVEL=INFO
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
API_V1_PREFIX=/api/v1
CORS_ORIGINS=*
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100
```

**重要**: 将数据库 URL 从 `postgresql://` 改为 `postgresql+asyncpg://`

示例:
```
# 原始 URL
postgresql://user:pass@host:5432/db

# 修改后
postgresql+asyncpg://user:pass@host:5432/db
```

### 6. 部署 (1分钟)

点击 "部署" 按钮，等待构建完成（约 2-3 分钟）。

### 7. 验证部署

访问以下地址验证：

- 健康检查: `https://your-app.anker-launch.com/health`
- API 文档: `https://your-app.anker-launch.com/api/docs`
- 前端页面: `https://your-app.anker-launch.com/`

## 常见问题

### 问题 1: 应用无法启动

检查环境变量是否正确设置，特别是：
- `DATABASE_URL` 格式必须是 `postgresql+asyncpg://`
- `JWT_SECRET_KEY` 不能为空

### 问题 2: 数据库连接失败

1. 确认数据库 URL 正确
2. 确认数据库已创建并可访问
3. 检查 URL 格式是否包含 `+asyncpg`

### 问题 3: 静态文件 404

检查项目的 `static/` 目录是否已提交到 Git。

## 需要帮助？

查看完整文档: [DEPLOYMENT.md](./DEPLOYMENT.md)

## 部署检查清单

部署前运行检查脚本：

```bash
./check-deployment.sh
```

确保所有检查通过后再部署。
