#!/bin/bash

# 运动管家 - 查看服务状态脚本

echo "📊 服务状态"
echo "================================"

PROJECT_DIR="/Users/admin/my-project"
cd "$PROJECT_DIR"

# 1. 检查服务器状态
echo "🐍 Python 服务器:"
if [ -f "$PROJECT_DIR/.server.pid" ]; then
    SERVER_PID=$(cat "$PROJECT_DIR/.server.pid")
    if ps -p $SERVER_PID > /dev/null 2>&1; then
        echo "   ✅ 运行中 (PID: $SERVER_PID)"
        echo "   📝 本地地址: http://localhost:8000"
    else
        echo "   ❌ 未运行 (PID 文件存在但进程不存在)"
    fi
else
    SERVER_PID=$(ps aux | grep "python -m src.main" | grep -v grep | awk '{print $2}' | head -1)
    if [ ! -z "$SERVER_PID" ]; then
        echo "   ⚠️  运行中但无 PID 文件 (PID: $SERVER_PID)"
        echo "   📝 本地地址: http://localhost:8000"
    else
        echo "   ❌ 未运行"
    fi
fi

echo ""

# 2. 检查隧道状态
echo "🌐 Cloudflare Tunnel:"
if [ -f "$PROJECT_DIR/.tunnel.pid" ]; then
    TUNNEL_PID=$(cat "$PROJECT_DIR/.tunnel.pid")
    if ps -p $TUNNEL_PID > /dev/null 2>&1; then
        echo "   ✅ 运行中 (PID: $TUNNEL_PID)"

        # 尝试从缓存文件读取 URL
        if [ -f "$PROJECT_DIR/.tunnel_url" ]; then
            TUNNEL_URL=$(cat "$PROJECT_DIR/.tunnel_url")
            echo "   🌐 公网地址: $TUNNEL_URL"
        else
            # 从日志文件提取 URL
            if [ -f "$PROJECT_DIR/tunnel.log" ]; then
                TUNNEL_URL=$(grep -o 'https://[^[:space:]]*trycloudflare.com' "$PROJECT_DIR/tunnel.log" | tail -1)
                if [ ! -z "$TUNNEL_URL" ]; then
                    echo "   🌐 公网地址: $TUNNEL_URL"
                    echo "$TUNNEL_URL" > "$PROJECT_DIR/.tunnel_url"
                else
                    echo "   ⚠️  隧道 URL 尚未生成，请稍等片刻后重试"
                fi
            else
                echo "   ⚠️  未找到隧道日志文件"
            fi
        fi
    else
        echo "   ❌ 未运行 (PID 文件存在但进程不存在)"
    fi
else
    TUNNEL_PID=$(ps aux | grep "cloudflared tunnel" | grep -v grep | awk '{print $2}' | head -1)
    if [ ! -z "$TUNNEL_PID" ]; then
        echo "   ⚠️  运行中但无 PID 文件 (PID: $TUNNEL_PID)"
        # 尝试从日志获取 URL
        if [ -f "$PROJECT_DIR/tunnel.log" ]; then
            TUNNEL_URL=$(grep -o 'https://[^[:space:]]*trycloudflare.com' "$PROJECT_DIR/tunnel.log" | tail -1)
            if [ ! -z "$TUNNEL_URL" ]; then
                echo "   🌐 公网地址: $TUNNEL_URL"
            fi
        fi
    else
        echo "   ❌ 未运行"
    fi
fi

echo ""
echo "================================"
echo "💡 提示:"
echo "   启动服务: ./start-background.sh"
echo "   停止服务: ./stop.sh"
echo "   查看服务器日志: tail -f server.log"
echo "   查看隧道日志: tail -f tunnel.log"
echo "================================"
