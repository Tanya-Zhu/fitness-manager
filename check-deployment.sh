#!/bin/bash
# 部署前检查脚本 - Pre-deployment Check Script

echo "🔍 运动管家 - 部署前检查"
echo "================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数
PASSED=0
FAILED=0
WARNINGS=0

# 检查函数
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2"
        ((FAILED++))
        return 1
    fi
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# 1. 检查必需文件
echo "1️⃣  检查必需文件..."
check_file "requirements.txt" "requirements.txt 存在"
check_file "runtime.txt" "runtime.txt 存在"
check_file "Procfile" "Procfile 存在"
check_file ".env.example" ".env.example 存在"
check_file ".env.production" ".env.production 存在"
check_file "alembic.ini" "alembic.ini 存在"
check_dir "alembic/versions" "数据库迁移脚本目录存在"
check_dir "static" "静态文件目录存在"
check_file "src/main.py" "应用入口文件存在"
echo ""

# 2. 检查 .env.production 配置
echo "2️⃣  检查环境变量配置..."
if [ -f ".env.production" ]; then
    # 检查是否包含默认密钥
    if grep -q "CHANGE_THIS_TO_A_SECURE_RANDOM_KEY" .env.production; then
        warn "JWT_SECRET_KEY 仍使用默认值，请更改为安全密钥"
    else
        echo -e "${GREEN}✓${NC} JWT_SECRET_KEY 已自定义"
        ((PASSED++))
    fi

    # 检查是否包含占位符
    if grep -q "username:password@hostname" .env.production; then
        warn "DATABASE_URL 包含占位符，部署时需要更新"
    else
        echo -e "${GREEN}✓${NC} DATABASE_URL 已配置"
        ((PASSED++))
    fi

    # 检查 APP_ENV
    if grep -q "APP_ENV=production" .env.production; then
        echo -e "${GREEN}✓${NC} APP_ENV 设置为 production"
        ((PASSED++))
    else
        warn "APP_ENV 未设置为 production"
    fi
fi
echo ""

# 3. 检查 .gitignore
echo "3️⃣  检查 .gitignore 配置..."
if [ -f ".gitignore" ]; then
    if grep -q "\.env$" .gitignore; then
        echo -e "${GREEN}✓${NC} .env 文件已忽略"
        ((PASSED++))
    else
        warn ".gitignore 未包含 .env"
    fi

    if grep -q "__pycache__" .gitignore; then
        echo -e "${GREEN}✓${NC} __pycache__ 已忽略"
        ((PASSED++))
    else
        warn ".gitignore 未包含 __pycache__"
    fi
else
    warn ".gitignore 文件不存在"
fi
echo ""

# 4. 检查 Git 状态
echo "4️⃣  检查 Git 状态..."
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Git 仓库已初始化"
    ((PASSED++))

    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        warn "有未提交的更改，建议提交后再部署"
        git status --short
    else
        echo -e "${GREEN}✓${NC} 所有更改已提交"
        ((PASSED++))
    fi
else
    warn "不是 Git 仓库"
fi
echo ""

# 5. 检查数据库迁移
echo "5️⃣  检查数据库迁移..."
MIGRATION_COUNT=$(ls -1 alembic/versions/*.py 2>/dev/null | wc -l)
if [ $MIGRATION_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓${NC} 找到 $MIGRATION_COUNT 个迁移脚本"
    ((PASSED++))
else
    warn "未找到数据库迁移脚本"
fi
echo ""

# 6. 检查依赖
echo "6️⃣  检查 Python 依赖..."
if [ -f "requirements.txt" ]; then
    DEPS=$(cat requirements.txt | grep -v "^#" | grep -v "^$" | wc -l)
    echo -e "${GREEN}✓${NC} 找到 $DEPS 个依赖包"
    ((PASSED++))

    # 检查关键依赖
    if grep -q "fastapi" requirements.txt; then
        echo -e "${GREEN}✓${NC} FastAPI 已包含"
        ((PASSED++))
    fi

    if grep -q "uvicorn" requirements.txt; then
        echo -e "${GREEN}✓${NC} Uvicorn 已包含"
        ((PASSED++))
    fi

    if grep -q "sqlalchemy" requirements.txt; then
        echo -e "${GREEN}✓${NC} SQLAlchemy 已包含"
        ((PASSED++))
    fi

    if grep -q "alembic" requirements.txt; then
        echo -e "${GREEN}✓${NC} Alembic 已包含"
        ((PASSED++))
    fi
fi
echo ""

# 7. 检查静态文件
echo "7️⃣  检查静态文件..."
if [ -d "static" ]; then
    STATIC_FILES=$(find static -type f | wc -l)
    if [ $STATIC_FILES -gt 0 ]; then
        echo -e "${GREEN}✓${NC} 找到 $STATIC_FILES 个静态文件"
        ((PASSED++))
    else
        warn "静态文件目录为空"
    fi
fi
echo ""

# 总结
echo "================================"
echo "📊 检查总结"
echo "================================"
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo -e "${YELLOW}警告: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}🎉 所有检查通过！可以开始部署。${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  有 $WARNINGS 个警告，请检查后再部署。${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ 有 $FAILED 个检查失败，请修复后再部署。${NC}"
    exit 1
fi
