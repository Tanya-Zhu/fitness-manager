#!/bin/bash
# 生产环境启动脚本
# Production startup script

set -e

echo "🚀 Starting Fitness Manager Application..."
echo "================================"

# 检查必需的环境变量
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL is not set!"
    echo "Please configure DATABASE_URL environment variable."
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "❌ ERROR: JWT_SECRET_KEY is not set!"
    echo "Please configure JWT_SECRET_KEY environment variable."
    exit 1
fi

echo "✅ Environment variables validated"

# 运行数据库迁移
echo ""
echo "📊 Running database migrations..."
alembic upgrade head || {
    echo "❌ Database migration failed!"
    echo "Please check your DATABASE_URL and database connection."
    exit 1
}
echo "✅ Database migrations completed"

# 启动应用
echo ""
echo "🌟 Starting FastAPI application..."
echo "   Host: 0.0.0.0"
echo "   Port: ${PORT:-8000}"
echo "================================"
echo ""

exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1
