#!/bin/bash

# 运动管家 - 快速启动脚本

echo "🏃 运动管家 - 启动脚本"
echo "================================"
echo ""

# Step 1: 检查 Docker
echo "📦 步骤 1/6: 检查 Docker..."
if ! docker ps &> /dev/null; then
    echo "❌ Docker 未运行"
    echo "   请先启动 Docker Desktop (Mac) 或 Docker 服务 (Linux)"
    echo "   然后重新运行此脚本"
    exit 1
fi
echo "✅ Docker 正在运行"
echo ""

# Step 2: 启动数据库和 Redis
echo "🗄️  步骤 2/6: 启动数据库和 Redis..."
docker-compose up -d
if [ $? -eq 0 ]; then
    echo "✅ 数据库和 Redis 已启动"
else
    echo "❌ 启动失败，请检查 docker-compose.yml"
    exit 1
fi
echo ""

# Step 3: 等待数据库就绪
echo "⏳ 步骤 3/6: 等待数据库就绪（5秒）..."
sleep 5
echo "✅ 数据库应该已就绪"
echo ""

# Step 4: 检查虚拟环境
echo "🐍 步骤 4/6: 检查 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "✅ 虚拟环境已创建"
fi
echo "✅ 虚拟环境存在"
echo ""

# Step 5: 激活虚拟环境并安装依赖
echo "📚 步骤 5/6: 安装依赖..."
source venv/bin/activate
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ 依赖已安装"
else
    echo "❌ 依赖安装失败"
    exit 1
fi
echo ""

# Step 6: 运行数据库迁移
echo "🔄 步骤 6/6: 运行数据库迁移..."
alembic upgrade head
if [ $? -eq 0 ]; then
    echo "✅ 数据库迁移完成"
else
    echo "⚠️  数据库迁移失败（如果是首次运行可能正常）"
fi
echo ""

# 完成
echo "================================"
echo "✨ 启动准备完成！"
echo ""
echo "现在启动应用服务器..."
echo "访问: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================"
echo ""

# 启动应用
python src/main.py
