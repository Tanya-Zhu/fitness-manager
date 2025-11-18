#!/bin/bash
# 创建部署包脚本
# Script to create deployment package

set -e

echo "📦 创建部署包..."
echo "================================"
echo ""

# 定义输出文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="fitness-manager-deploy-${TIMESTAMP}.tar.gz"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
PROJECT_NAME="fitness-manager"
DEPLOY_DIR="${TEMP_DIR}/${PROJECT_NAME}"

echo "📁 准备部署文件..."

# 创建部署目录
mkdir -p "${DEPLOY_DIR}"

# 复制必需的文件和目录
echo "  ├─ 复制源代码..."
cp -r src "${DEPLOY_DIR}/"

echo "  ├─ 复制静态文件..."
cp -r static "${DEPLOY_DIR}/"

echo "  ├─ 复制数据库迁移..."
cp -r alembic "${DEPLOY_DIR}/"

echo "  ├─ 复制配置文件..."
cp requirements.txt "${DEPLOY_DIR}/"
cp runtime.txt "${DEPLOY_DIR}/"
cp Procfile "${DEPLOY_DIR}/"
cp alembic.ini "${DEPLOY_DIR}/"
cp .env.production "${DEPLOY_DIR}/"
cp .env.example "${DEPLOY_DIR}/"

# 复制可选文件（如果存在）
[ -f app.yaml ] && cp app.yaml "${DEPLOY_DIR}/"
[ -f pyproject.toml ] && cp pyproject.toml "${DEPLOY_DIR}/"
[ -f .flake8 ] && cp .flake8 "${DEPLOY_DIR}/"

# 复制文档
echo "  ├─ 复制文档..."
[ -f DEPLOYMENT.md ] && cp DEPLOYMENT.md "${DEPLOY_DIR}/"
[ -f DEPLOY_QUICK_START.md ] && cp DEPLOY_QUICK_START.md "${DEPLOY_DIR}/"
[ -f CLAUDE.md ] && cp CLAUDE.md "${DEPLOY_DIR}/"
[ -f README.md ] && cp README.md "${DEPLOY_DIR}/"

# 清理 Python 缓存
echo "  └─ 清理缓存文件..."
find "${DEPLOY_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "${DEPLOY_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true
find "${DEPLOY_DIR}" -type f -name "*.pyo" -delete 2>/dev/null || true
find "${DEPLOY_DIR}" -type f -name ".DS_Store" -delete 2>/dev/null || true

echo ""
echo "📊 包内容统计..."

# 统计文件
FILE_COUNT=$(find "${DEPLOY_DIR}" -type f | wc -l | tr -d ' ')
DIR_COUNT=$(find "${DEPLOY_DIR}" -type d | wc -l | tr -d ' ')

echo "  ├─ 文件数: ${FILE_COUNT}"
echo "  └─ 目录数: ${DIR_COUNT}"

echo ""
echo "🗜️  压缩打包..."

# 打包
cd "${TEMP_DIR}"
tar -czf "${OUTPUT_FILE}" "${PROJECT_NAME}"

# 移动到项目目录
mv "${OUTPUT_FILE}" "${OLDPWD}/"
cd "${OLDPWD}"

# 清理临时目录
rm -rf "${TEMP_DIR}"

# 显示结果
PACKAGE_SIZE=$(du -h "${OUTPUT_FILE}" | cut -f1)

echo ""
echo "================================"
echo "✅ 部署包创建成功！"
echo "================================"
echo ""
echo "📦 文件名: ${OUTPUT_FILE}"
echo "📏 大小: ${PACKAGE_SIZE}"
echo "📍 位置: $(pwd)/${OUTPUT_FILE}"
echo ""
echo "下一步操作："
echo "1. 登录 anker-launch 平台: https://go.anker-launch.com/dashboard"
echo "2. 创建新应用或选择现有应用"
echo "3. 选择 '手动上传' 部署方式"
echo "4. 上传文件: ${OUTPUT_FILE}"
echo "5. 配置环境变量（参考 DEPLOYMENT.md）"
echo "6. 点击部署"
echo ""
echo "⚠️  重要提醒："
echo "   - 部署前请先在平台配置所有必需的环境变量"
echo "   - 特别是 DATABASE_URL 和 JWT_SECRET_KEY"
echo "   - 详细说明请查看 DEPLOY_QUICK_START.md"
echo ""
