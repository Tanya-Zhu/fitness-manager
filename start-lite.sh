#!/bin/bash

# 运动管家 - 轻量版启动脚本（无需 Docker）

echo "🏃 运动管家 - 轻量版启动"
echo "================================"
echo "✨ 无需 Docker，立即可用！"
echo ""

# Step 1: 检查虚拟环境
echo "🐍 步骤 1/4: 检查 Python 虚拟环境..."
if [ ! -d "venv" ]; then
    echo "⚠️  虚拟环境不存在，正在创建..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo "✅ 虚拟环境已创建"
    else
        echo "❌ 虚拟环境创建失败"
        exit 1
    fi
else
    echo "✅ 虚拟环境已存在"
fi
echo ""

# Step 2: 激活虚拟环境
echo "🔄 步骤 2/4: 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# Step 3: 安装依赖
echo "📚 步骤 3/4: 安装依赖..."
pip install -q -r requirements.txt
pip install -q aiosqlite  # SQLite 异步驱动
pip install -q 'bcrypt>=4.0.0,<5.0.0'  # bcrypt 4.x for passlib compatibility
pip install -q greenlet email-validator  # Additional dependencies
if [ $? -eq 0 ]; then
    echo "✅ 依赖已安装"
else
    echo "❌ 依赖安装失败"
    exit 1
fi
echo ""

# Step 4: 初始化数据库
echo "🔄 步骤 4/4: 初始化 SQLite 数据库..."
alembic upgrade head
if [ $? -eq 0 ]; then
    echo "✅ 数据库已初始化"
else
    echo "⚠️  数据库迁移失败（如果是首次运行可能正常）"
fi
echo ""

# 完成
echo "================================"
echo "✨ 轻量版启动准备完成！"
echo ""
echo "📦 使用技术："
echo "   - 数据库: SQLite (fitness.db)"
echo "   - 调度器: 内存存储"
echo "   - 无需 Docker"
echo ""
echo "⚠️  注意："
echo "   - 提醒功能仅在应用运行时有效"
echo "   - 关闭应用后，定时提醒会失效"
echo ""
echo "现在启动应用服务器..."
echo "访问: http://localhost:8000"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================"
echo ""

# 启动应用
cd /Users/admin/my-project
python -m src.main
