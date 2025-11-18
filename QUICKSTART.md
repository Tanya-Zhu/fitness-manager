# 🚀 快速启动（2步）

## 问题诊断结果

我已经检查了你的项目，发现了以下问题：

- ❌ `.env` 文件缺失 → **已自动修复**
- ❌ Docker 未运行 → **需要你手动启动**
- ❌ 虚拟环境未创建 → **启动脚本会自动处理**

---

## 只需2步启动

### 第1步：启动 Docker

**Mac 用户**：
```bash
# 打开 Docker Desktop 应用
# 等待 Docker 图标变绿（表示正在运行）
```

**Linux 用户**：
```bash
sudo systemctl start docker
```

**验证 Docker 是否运行**：
```bash
docker ps
# 如果能看到表格输出（即使是空的），说明 Docker 正在运行
```

### 第2步：运行启动脚本

```bash
./start.sh
```

这个脚本会自动完成：
- ✅ 启动 PostgreSQL 和 Redis
- ✅ 创建 Python 虚拟环境（如果不存在）
- ✅ 安装所有依赖
- ✅ 运行数据库迁移
- ✅ 启动 FastAPI 应用

---

## 访问网页

当你看到这样的输出：

```
🚀 Application starting...
📝 Environment: development
📖 API Documentation: http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**打开浏览器，访问：http://localhost:8000**

你会看到登录页面！

---

## 使用应用

### 首次使用

1. 点击"立即注册"
2. 填写邮箱和密码（至少8位）
3. 注册成功后返回登录页
4. 使用刚注册的账号登录
5. 开始创建你的健身计划！

### 演示账号

如果你想快速测试，可以注册这个账号：
- 邮箱：`demo@example.com`
- 密码：`password123`

---

## 停止应用

在终端按 `Ctrl + C` 停止应用

如果要停止 Docker 服务：
```bash
docker-compose down
```

---

## 遇到问题？

### 问题1：Docker 无法启动
```bash
# Mac: 重新安装 Docker Desktop
# Linux: sudo systemctl status docker
```

### 问题2：端口8000被占用
```bash
# 查找占用进程
lsof -i :8000

# 杀死进程（替换 PID）
kill -9 <PID>
```

### 问题3：启动脚本权限错误
```bash
chmod +x start.sh
./start.sh
```

### 更多问题？

查看详细文档：
- `START.md` - 完整的启动和故障排除指南
- `WEB_GUIDE.md` - 网页版使用指南
- `USAGE_GUIDE.md` - API 使用指南

---

## 技术栈

- **后端**: FastAPI + PostgreSQL + Redis
- **前端**: HTML + JavaScript + Tailwind CSS
- **认证**: JWT (Bearer Token)
- **调度**: APScheduler

---

## 项目结构

```
my-project/
├── src/              # 后端代码
│   ├── main.py       # 应用入口
│   ├── api/          # API 路由
│   ├── core/         # 核心配置
│   ├── models/       # 数据库模型
│   └── services/     # 业务逻辑
├── static/           # 前端代码
│   ├── index.html    # 主页
│   ├── login.html    # 登录页
│   ├── register.html # 注册页
│   └── js/api.js     # API 封装
├── alembic/          # 数据库迁移
├── .env              # 环境变量 ✅ 已创建
├── docker-compose.yml# Docker 配置
└── start.sh          # 启动脚本 ✅ 已创建
```

---

## 现在开始

**只需一条命令**（确保 Docker 已运行）：

```bash
./start.sh
```

然后访问 **http://localhost:8000** 🎉
