#!/bin/bash

# 运动管家 - 停止后台服务脚本

echo "🛑 停止后台服务..."
echo "================================"

PROJECT_DIR="/Users/admin/my-project"
cd "$PROJECT_DIR"

STOPPED=0

# 1. 停止服务器
if [ -f "$PROJECT_DIR/.server.pid" ]; then
    SERVER_PID=$(cat "$PROJECT_DIR/.server.pid")
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        echo "🐍 停止服务器 (PID: $SERVER_PID)..."
        kill $SERVER_PID
        sleep 2
        if ps -p $SERVER_PID > /dev/null 2>&1; then
            echo "   强制停止..."
            kill -9 $SERVER_PID
        fi
        echo "✅ 服务器已停止"
        STOPPED=1
    else
        echo "⚠️  服务器进程不存在 (PID: $SERVER_PID)"
    fi
    rm -f "$PROJECT_DIR/.server.pid"
else
    echo "⚠️  未找到服务器 PID 文件"
fi

# 2. 停止隧道
echo ""
if [ -f "$PROJECT_DIR/.tunnel.pid" ]; then
    TUNNEL_PID=$(cat "$PROJECT_DIR/.tunnel.pid")
    if ps -p $TUNNEL_PID > /dev/null 2>&1; then
        echo "🌐 停止 Cloudflare Tunnel (PID: $TUNNEL_PID)..."
        kill $TUNNEL_PID
        sleep 2
        if ps -p $TUNNEL_PID > /dev/null 2>&1; then
            echo "   强制停止..."
            kill -9 $TUNNEL_PID
        fi
        echo "✅ 隧道已停止"
        STOPPED=1
    else
        echo "⚠️  隧道进程不存在 (PID: $TUNNEL_PID)"
    fi
    rm -f "$PROJECT_DIR/.tunnel.pid"
else
    echo "⚠️  未找到隧道 PID 文件"
fi

# 3. 清理其他可能的进程
echo ""
echo "🔍 检查其他相关进程..."
OTHER_SERVER=$(ps aux | grep "python -m src.main" | grep -v grep | awk '{print $2}')
OTHER_TUNNEL=$(ps aux | grep "cloudflared tunnel" | grep -v grep | awk '{print $2}')

if [ ! -z "$OTHER_SERVER" ]; then
    echo "   发现其他服务器进程: $OTHER_SERVER，正在停止..."
    kill $OTHER_SERVER 2>/dev/null
    STOPPED=1
fi

if [ ! -z "$OTHER_TUNNEL" ]; then
    echo "   发现其他隧道进程: $OTHER_TUNNEL，正在停止..."
    kill $OTHER_TUNNEL 2>/dev/null
    STOPPED=1
fi

# 4. 清理 URL 文件
rm -f "$PROJECT_DIR/.tunnel_url"

echo ""
echo "================================"
if [ $STOPPED -eq 1 ]; then
    echo "✅ 所有服务已停止"
else
    echo "ℹ️  没有运行中的服务"
fi
echo "================================"
