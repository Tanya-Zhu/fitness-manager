#!/bin/bash

# 运动管家 - 后台持续运行脚本

echo "🚀 启动后台服务..."
echo "================================"

# 获取项目目录
PROJECT_DIR="/Users/admin/my-project"
cd "$PROJECT_DIR"

# 1. 检查并停止旧进程
echo "📋 检查现有进程..."
OLD_SERVER_PID=$(ps aux | grep "python -m src.main" | grep -v grep | awk '{print $2}' | head -1)
OLD_TUNNEL_PID=$(ps aux | grep "cloudflared tunnel" | grep -v grep | awk '{print $2}' | head -1)

if [ ! -z "$OLD_SERVER_PID" ]; then
    echo "⚠️  发现旧的服务器进程 (PID: $OLD_SERVER_PID)，正在停止..."
    kill $OLD_SERVER_PID 2>/dev/null
    sleep 2
fi

if [ ! -z "$OLD_TUNNEL_PID" ]; then
    echo "⚠️  发现旧的隧道进程 (PID: $OLD_TUNNEL_PID)，正在停止..."
    kill $OLD_TUNNEL_PID 2>/dev/null
    sleep 2
fi

# 2. 激活虚拟环境并启动服务器
echo ""
echo "🐍 启动 Python 服务器..."
source venv/bin/activate
nohup python -m src.main > "$PROJECT_DIR/server.log" 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > "$PROJECT_DIR/.server.pid"
echo "✅ 服务器已启动 (PID: $SERVER_PID)"
echo "   日志文件: $PROJECT_DIR/server.log"

# 3. 等待服务器启动
echo ""
echo "⏳ 等待服务器就绪..."
sleep 5

# 4. 启动 Cloudflare Tunnel
echo ""
echo "🌐 启动 Cloudflare Tunnel..."
nohup ~/bin/cloudflared tunnel --url http://localhost:8000 > "$PROJECT_DIR/tunnel.log" 2>&1 &
TUNNEL_PID=$!
echo $TUNNEL_PID > "$PROJECT_DIR/.tunnel.pid"
echo "✅ 隧道已启动 (PID: $TUNNEL_PID)"
echo "   日志文件: $PROJECT_DIR/tunnel.log"

# 5. 等待隧道建立并获取 URL
echo ""
echo "⏳ 等待隧道建立（10秒）..."
sleep 10

# 6. 提取并显示 URL
echo ""
echo "================================"
echo "✨ 服务已在后台启动！"
echo ""
echo "📊 进程信息:"
echo "   服务器 PID: $SERVER_PID"
echo "   隧道 PID: $TUNNEL_PID"
echo ""

TUNNEL_URL=$(grep -o 'https://[^[:space:]]*trycloudflare.com' "$PROJECT_DIR/tunnel.log" | head -1)
if [ ! -z "$TUNNEL_URL" ]; then
    echo "🌐 公网访问地址:"
    echo "   $TUNNEL_URL"
    echo ""
    echo "$TUNNEL_URL" > "$PROJECT_DIR/.tunnel_url"
else
    echo "⚠️  隧道 URL 尚未生成，请稍后运行: ./status.sh"
fi

echo "📝 本地访问地址:"
echo "   http://localhost:8000"
echo ""
echo "🔍 查看状态: ./status.sh"
echo "🛑 停止服务: ./stop.sh"
echo "📋 查看日志: tail -f server.log 或 tail -f tunnel.log"
echo "================================"
