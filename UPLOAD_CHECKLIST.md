# 📋 上传部署检查清单

使用此清单确保上传部署的每个步骤都已完成。

## 准备阶段

- [x] 部署包已创建: `fitness-manager-deploy-*.tar.gz` (70KB)
- [ ] 已登录 anker-launch 平台: https://go.anker-launch.com/dashboard
- [ ] 已生成 JWT 密钥: 运行 `openssl rand -hex 32`

## 平台配置

- [ ] 创建或选择应用
- [ ] 创建 PostgreSQL 数据库
- [ ] 获取数据库连接字符串
- [ ] 将数据库 URL 从 `postgresql://` 改为 `postgresql+asyncpg://`

## 环境变量配置

### 必需配置 (3个)

- [ ] `APP_ENV` = `production`
- [ ] `DATABASE_URL` = `postgresql+asyncpg://user:pass@host:5432/db`
- [ ] `JWT_SECRET_KEY` = `<生成的32字节密钥>`

### 推荐配置 (可选)

- [ ] `REDIS_URL` = `memory://` (或 Redis 连接字符串)
- [ ] `LOG_LEVEL` = `INFO`
- [ ] `CORS_ORIGINS` = `*` (或具体域名)

## 上传部署

- [ ] 选择 "手动上传" 方式
- [ ] 上传 `fitness-manager-deploy-*.tar.gz`
- [ ] 确认上传成功
- [ ] 点击 "部署" 按钮
- [ ] 等待构建完成 (3-5分钟)

## 验证部署

- [ ] 应用状态显示 "Running" 或 "活跃"
- [ ] 健康检查通过: `/health` 返回 `{"status": "healthy"}`
- [ ] API 文档可访问: `/api/docs`
- [ ] 前端页面可访问: `/`
- [ ] 查看日志确认无错误

## 日志检查要点

启动成功应看到：
```
✅ 🚀 Application starting...
✅ 📝 Environment: production
✅ 数据库连接成功
✅ ⏰ APScheduler started successfully
```

## 故障排查

如遇问题，按顺序检查：

1. [ ] 查看部署日志中的错误信息
2. [ ] 确认所有必需环境变量已配置
3. [ ] 确认数据库 URL 格式正确 (包含 `+asyncpg`)
4. [ ] 确认数据库可访问
5. [ ] 参考 [UPLOAD_GUIDE.md](./UPLOAD_GUIDE.md) 故障排查章节

## 部署后

- [ ] 测试注册功能
- [ ] 测试登录功能
- [ ] 测试创建健身计划
- [ ] 配置域名 (如需要)
- [ ] 设置监控告警
- [ ] 配置数据库备份

## 安全检查

- [ ] JWT_SECRET_KEY 使用强密钥
- [ ] 数据库密码足够强
- [ ] CORS_ORIGINS 仅包含信任的域名
- [ ] 本地 .env 文件未提交到 Git
- [ ] 定期备份数据库

---

## 快速命令参考

```bash
# 重新生成 JWT 密钥
openssl rand -hex 32

# 重新打包
./create-deploy-package.sh

# 检查本地部署配置
./check-deployment.sh

# 测试健康检查
curl https://your-app.anker-launch.com/health
```

## 文档链接

- 📘 完整上传指南: [UPLOAD_GUIDE.md](./UPLOAD_GUIDE.md)
- 🚀 快速部署: [DEPLOY_QUICK_START.md](./DEPLOY_QUICK_START.md)
- 📖 详细文档: [DEPLOYMENT.md](./DEPLOYMENT.md)
