# 🚀 快速启动指南

## 检查清单

在启动前，请确保：

- [ ] Python 3.11+ 已安装
- [ ] Docker 已安装并运行
- [ ] 虚拟环境已创建
- [ ] 依赖已安装

---

## 第一步：检查 Docker 是否运行

```bash
# 检查 Docker 是否在运行
docker ps

# 如果没有运行，启动 Docker Desktop（Mac）或 Docker 服务（Linux）
```

---

## 第二步：启动数据库和 Redis

```bash
# 在项目根目录下运行
docker-compose up -d

# 验证服务是否正常
docker-compose ps

# 应该看到 postgres 和 redis 两个服务都是 "Up" 状态
```

---

## 第三步：创建虚拟环境（如果还没创建）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Mac/Linux:
source venv/bin/activate

# Windows:
# venv\Scripts\activate
```

---

## 第四步：安装依赖

```bash
# 确保虚拟环境已激活（命令行前面应该有 (venv)）
pip install -r requirements.txt
```

---

## 第五步：配置环境变量

```bash
# 如果还没有 .env 文件，复制示例文件
cp .env.example .env

# 编辑 .env 文件，确保配置正确
# 重要配置：
# - DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/fitness_db
# - REDIS_URL=redis://localhost:6379/0
# - JWT_SECRET_KEY=your-secret-key-change-this-in-production
```

---

## 第六步：运行数据库迁移

```bash
# 初始化数据库表
alembic upgrade head

# 如果出错，检查数据库连接
```

---

## 第七步：启动应用

```bash
# 启动 FastAPI 应用
python src/main.py

# 或者使用 uvicorn
# uvicorn src.main:app --reload
```

---

## 第八步：访问网页

应用启动成功后，你会看到：

```
🚀 Application starting...
📝 Environment: development
📖 API Documentation: http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**现在打开浏览器，访问：**

👉 **http://localhost:8000**

你应该会看到登录页面！

---

## 🔍 问题排查

### 问题1: 端口被占用

**错误信息**: `OSError: [Errno 48] Address already in use`

**解决方法**:
```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 杀死该进程（替换 PID 为实际进程ID）
kill -9 <PID>

# 或者使用不同端口启动
uvicorn src.main:app --port 8001
```

### 问题2: 数据库连接失败

**错误信息**: `connection refused` 或 `could not connect to server`

**解决方法**:
```bash
# 检查 docker-compose 服务状态
docker-compose ps

# 如果没有运行，启动服务
docker-compose up -d

# 查看 PostgreSQL 日志
docker-compose logs postgres

# 重启数据库
docker-compose restart postgres
```

### 问题3: 模块找不到

**错误信息**: `ModuleNotFoundError: No module named 'fastapi'`

**解决方法**:
```bash
# 确认虚拟环境已激活
which python
# 应该显示 /path/to/your/project/venv/bin/python

# 重新安装依赖
pip install -r requirements.txt
```

### 问题4: Alembic 迁移失败

**错误信息**: `Target database is not up to date`

**解决方法**:
```bash
# 查看当前迁移状态
alembic current

# 查看所有迁移版本
alembic history

# 升级到最新版本
alembic upgrade head

# 如果还有问题，可以重置（警告：会删除数据）
docker-compose down -v
docker-compose up -d
alembic upgrade head
```

### 问题5: 页面加载但显示 404

**原因**: 静态文件路径配置问题

**解决方法**:
```bash
# 检查 static 目录是否存在
ls -la static/

# 应该看到：
# - index.html
# - login.html
# - register.html
# - create-plan.html
# - plan-detail.html
# - js/api.js
```

### 问题6: 登录后立即退出

**原因**: JWT_SECRET_KEY 配置问题

**解决方法**:
```bash
# 编辑 .env 文件
nano .env

# 确保有这一行（不要用默认值）
JWT_SECRET_KEY=your-very-secure-secret-key-min-32-chars

# 重启应用
```

---

## 🧪 验证安装

运行这些命令验证一切正常：

```bash
# 1. 检查 Python 版本
python --version
# 应该是 3.11 或更高

# 2. 检查虚拟环境
which python
# 应该指向 venv 目录

# 3. 检查 Docker 服务
docker-compose ps
# postgres 和 redis 应该都是 Up

# 4. 检查数据库连接
docker exec -it my-project-postgres-1 psql -U user -d fitness_db -c "SELECT 1;"
# 应该返回 1

# 5. 测试健康检查
curl http://localhost:8000/health
# 应该返回 {"status":"healthy"}
```

---

## 📖 快速测试流程

启动成功后：

1. **访问** http://localhost:8000
2. **点击** "立即注册"
3. **填写** 邮箱: test@example.com, 密码: password123
4. **登录** 使用刚注册的账号
5. **创建计划** 点击"创建新计划"
6. **完成！**

---

## 🆘 仍然无法启动？

运行以下诊断命令并提供输出：

```bash
# 完整诊断
echo "=== Python 版本 ==="
python --version

echo "=== 虚拟环境 ==="
which python

echo "=== Docker 状态 ==="
docker-compose ps

echo "=== 端口占用 ==="
lsof -i :8000

echo "=== 静态文件 ==="
ls -la static/

echo "=== 环境变量 ==="
cat .env | grep -v SECRET

echo "=== 数据库连接 ==="
docker exec my-project-postgres-1 psql -U user -d fitness_db -c "SELECT version();"
```

把输出发给我，我会帮你诊断！
