# 手动上传部署指南

本指南提供通过手动上传的方式将应用部署到 anker-launch 平台的详细步骤。

## 📦 第一步：部署包已就绪

✅ 部署包已创建完成：`fitness-manager-deploy-*.tar.gz`

如需重新打包，运行：
```bash
./create-deploy-package.sh
```

## 🌐 第二步：登录 anker-launch 平台

1. 打开浏览器访问: https://go.anker-launch.com/dashboard
2. 使用您的账号登录

## 🚀 第三步：创建/选择应用

### 如果是新应用：

1. 点击 **"新建应用"** 或 **"Create New App"** 按钮
2. 填写应用信息：
   - 应用名称: `fitness-manager` 或您喜欢的名称
   - 应用描述: `健身计划管理系统`
   - 区域: 选择离您最近的区域
3. 点击创建

### 如果是已有应用：

1. 在应用列表中找到您的应用
2. 点击进入应用详情页

## 📤 第四步：上传部署包

1. 在应用页面找到 **"部署"** 或 **"Deploy"** 选项
2. 选择部署方式: **"手动上传"** 或 **"Upload"**
3. 点击 **"选择文件"** 或 **"Choose File"** 按钮
4. 选择刚才创建的文件: `fitness-manager-deploy-*.tar.gz`
5. 点击 **"上传"** 按钮

上传可能需要几秒到几分钟，取决于网络速度。

## 🗄️ 第五步：配置数据库

### 创建数据库实例

1. 在应用设置页面找到 **"数据库"** 或 **"Database"** 选项
2. 点击 **"添加数据库"** 或 **"Add Database"**
3. 选择 **PostgreSQL**
4. 配置数据库：
   - 版本: 选择 PostgreSQL 15 或更高
   - 名称: `fitness_db` 或其他名称
5. 点击创建并等待数据库就绪

### 获取数据库连接信息

1. 数据库创建完成后，点击查看详情
2. 复制 **连接字符串** (Connection String)
3. 连接字符串格式通常为: `postgresql://user:pass@host:5432/dbname`

**重要**: 需要将 `postgresql://` 改为 `postgresql+asyncpg://`

示例转换：
```
原始: postgresql://user:pass@host.anker-launch.com:5432/fitness_db
修改: postgresql+asyncpg://user:pass@host.anker-launch.com:5432/fitness_db
```

## 🔐 第六步：配置环境变量

### 生成 JWT 密钥

在本地终端运行：
```bash
openssl rand -hex 32
```

复制输出的字符串（例如: `a3f2...d8c9`）

### 在平台设置环境变量

1. 在应用设置页面找到 **"环境变量"** 或 **"Environment Variables"**
2. 点击 **"添加变量"** 或 **"Add Variable"**
3. 逐个添加以下环境变量：

#### 必需变量（务必配置）：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `APP_ENV` | `production` | 应用环境 |
| `DATABASE_URL` | `postgresql+asyncpg://...` | 从步骤五获取并修改 |
| `JWT_SECRET_KEY` | `<刚才生成的密钥>` | JWT 加密密钥 |

#### 推荐变量（有默认值，可选配置）：

| 变量名 | 推荐值 | 说明 |
|--------|--------|------|
| `REDIS_URL` | `memory://` | 使用内存存储（或配置 Redis） |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `JWT_ALGORITHM` | `HS256` | JWT 算法 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | 访问令牌过期时间 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | 刷新令牌过期天数 |
| `API_V1_PREFIX` | `/api/v1` | API 路径前缀 |
| `CORS_ORIGINS` | `*` | 允许的跨域来源 |

### 配置 Redis（可选但推荐）

如果平台提供 Redis 服务：

1. 在应用设置中添加 Redis 实例
2. 获取 Redis 连接字符串（如: `redis://host:6379/0`）
3. 将其设置为 `REDIS_URL` 环境变量

如果不配置 Redis，应用会自动使用内存模式（功能受限）。

## 🚀 第七步：启动部署

1. 确认所有环境变量已正确配置
2. 点击 **"部署"** 或 **"Deploy"** 按钮
3. 等待构建和部署完成（通常 3-5 分钟）

### 部署过程说明

平台会自动执行以下步骤：
1. 解压上传的文件
2. 安装 Python 依赖 (`pip install -r requirements.txt`)
3. 运行数据库迁移 (`alembic upgrade head`)
4. 启动应用 (`uvicorn`)

您可以在部署日志中查看详细进度。

## ✅ 第八步：验证部署

### 1. 检查应用状态

在应用页面查看应用状态，应显示为 **"Running"** 或 **"活跃"**。

### 2. 获取应用 URL

在应用详情页复制应用访问地址，通常格式为：
```
https://your-app-name.anker-launch.com
```

### 3. 测试健康检查

在浏览器访问或使用 curl：
```bash
curl https://your-app-name.anker-launch.com/health
```

预期响应：
```json
{
  "status": "healthy",
  "timestamp": "2024-11-17T..."
}
```

### 4. 访问 API 文档

访问 Swagger 文档页面：
```
https://your-app-name.anker-launch.com/api/docs
```

应该能看到完整的 API 文档界面。

### 5. 访问前端页面

访问应用根路径：
```
https://your-app-name.anker-launch.com/
```

应该能看到前端界面。

## 📊 查看日志

### 实时日志

1. 在应用页面找到 **"日志"** 或 **"Logs"** 选项
2. 查看应用启动日志和运行日志

### 关键日志信息

启动成功的日志应包含：
```
🚀 Application starting...
📝 Environment: production
数据库连接成功
⏰ APScheduler started successfully
```

## ❌ 故障排查

### 问题 1: 应用无法启动

**可能原因**:
- 环境变量配置错误
- 数据库连接失败

**解决方案**:
1. 检查日志中的错误信息
2. 确认 `DATABASE_URL` 格式正确（包含 `+asyncpg`）
3. 确认 `JWT_SECRET_KEY` 已设置

### 问题 2: 数据库迁移失败

**错误信息**: `relation does not exist` 或类似

**解决方案**:
1. 确认数据库已创建并可访问
2. 在平台终端手动运行迁移：
   ```bash
   alembic upgrade head
   ```

### 问题 3: 静态文件 404

**错误**: 访问 `/` 返回 404

**解决方案**:
1. 确认 `static/` 目录已包含在部署包中
2. 重新打包并上传

### 问题 4: CORS 错误

**错误**: 前端请求 API 时跨域错误

**解决方案**:
更新 `CORS_ORIGINS` 环境变量，添加前端域名：
```
CORS_ORIGINS=https://your-frontend.com,https://go.anker-launch.com
```

### 问题 5: 端口配置问题

**错误**: 应用监听了错误的端口

**解决方案**:
确认 `Procfile` 中使用了 `${PORT}` 变量：
```
web: uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

## 🔄 更新应用

当需要更新应用时：

1. 修改代码
2. 重新打包：
   ```bash
   ./create-deploy-package.sh
   ```
3. 在平台上传新的部署包
4. 点击部署

平台会自动执行滚动更新，确保零停机时间。

## 🗑️ 重新开始

如果需要完全重新部署：

1. 删除现有应用（可选）
2. 重新运行打包脚本
3. 按照本指南从头开始

## 📞 获取帮助

- 查看完整文档: [DEPLOYMENT.md](./DEPLOYMENT.md)
- 快速开始: [DEPLOY_QUICK_START.md](./DEPLOY_QUICK_START.md)
- anker-launch 平台文档: https://go.anker-launch.com/docs

## 🎉 部署完成！

恭喜！如果所有步骤都成功，您的应用现在已经在 anker-launch 平台上运行了。

现在您可以：
- 分享应用 URL 给用户
- 配置自定义域名（如果平台支持）
- 设置监控和告警
- 查看应用性能指标

---

**安全提醒**:
- ✅ 定期更新 JWT 密钥
- ✅ 不要在公开场合分享环境变量
- ✅ 定期备份数据库
- ✅ 监控应用日志和性能
