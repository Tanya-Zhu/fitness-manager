#!/bin/bash

# 快速获取当前公网访问地址

PROJECT_DIR="/Users/admin/my-project"
cd "$PROJECT_DIR"

echo "🌐 运动管家 - 当前访问地址"
echo "================================"

# 检查服务器状态
if [ -f "$PROJECT_DIR/.server.pid" ]; then
    SERVER_PID=$(cat "$PROJECT_DIR/.server.pid")
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        echo "✅ 服务器运行中 (PID: $SERVER_PID)"
        echo "📝 本地地址: http://localhost:8000"
    else
        echo "❌ 服务器未运行"
    fi
else
    echo "❌ 服务器未运行"
fi

echo ""

# 检查隧道状态
if [ -f "$PROJECT_DIR/.tunnel.pid" ]; then
    TUNNEL_PID=$(cat "$PROJECT_DIR/.tunnel.pid")
    if ps -p $TUNNEL_PID > /dev/null 2>&1; then
        echo "✅ 隧道运行中 (PID: $TUNNEL_PID)"

        # 从缓存获取URL
        if [ -f "$PROJECT_DIR/.tunnel_url" ]; then
            TUNNEL_URL=$(cat "$PROJECT_DIR/.tunnel_url")
            echo "🌐 公网地址: $TUNNEL_URL"
            echo ""
            echo "📱 快速访问链接:"
            echo "   登录: ${TUNNEL_URL}/login.html"
            echo "   注册: ${TUNNEL_URL}/register.html"
            echo "   首页: ${TUNNEL_URL}/"
        else
            echo "⚠️  正在获取隧道地址..."
            sleep 3
            TUNNEL_URL=$(grep -o 'https://[^[:space:]]*trycloudflare.com' "$PROJECT_DIR/tunnel.log" | tail -1)
            if [ ! -z "$TUNNEL_URL" ]; then
                echo "🌐 公网地址: $TUNNEL_URL"
                echo "$TUNNEL_URL" > "$PROJECT_DIR/.tunnel_url"
            else
                echo "⚠️  无法获取隧道地址，请查看日志: tail -f tunnel.log"
            fi
        fi
    else
        echo "❌ 隧道未运行"
    fi
else
    echo "❌ 隧道未运行"
fi

echo ""

# 检查监控状态
MONITOR_PID=$(ps aux | grep "bash.*monitor.sh" | grep -v grep | awk '{print $2}' | head -1)
if [ ! -z "$MONITOR_PID" ]; then
    echo "🔍 监控服务运行中 (PID: $MONITOR_PID)"
else
    echo "⚠️  监控服务未启动"
    echo "   启动监控: ./start-monitor.sh"
fi

echo ""
echo "================================"
echo "💡 提示:"
echo "   启动服务: ./start-background.sh"
echo "   停止服务: ./stop.sh"
echo "   启动监控: ./start-monitor.sh"
echo "   查看日志: tail -f monitor.log"
echo "================================"
