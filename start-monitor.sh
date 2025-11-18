#!/bin/bash

# 启动监控服务

PROJECT_DIR="/Users/admin/my-project"
cd "$PROJECT_DIR"

# 检查监控是否已经在运行
MONITOR_PID=$(ps aux | grep "bash.*monitor.sh" | grep -v grep | awk '{print $2}' | head -1)

if [ ! -z "$MONITOR_PID" ]; then
    echo "⚠️  监控服务已经在运行 (PID: $MONITOR_PID)"
    echo "   如需重启，请先运行: ./stop-monitor.sh"
    exit 0
fi

echo "🔍 启动隧道监控服务..."
nohup bash "$PROJECT_DIR/monitor.sh" > /dev/null 2>&1 &
MONITOR_PID=$!
echo $MONITOR_PID > "$PROJECT_DIR/.monitor.pid"

sleep 2

if ps -p $MONITOR_PID > /dev/null 2>&1; then
    echo "✅ 监控服务已启动 (PID: $MONITOR_PID)"
    echo ""
    echo "📊 监控功能："
    echo "   - 每分钟检查隧道状态"
    echo "   - 连续失败3次自动重启"
    echo "   - 隧道进程异常自动重启"
    echo ""
    echo "📋 查看监控日志: tail -f monitor.log"
    echo "🛑 停止监控: ./stop-monitor.sh"
else
    echo "❌ 监控服务启动失败"
    rm -f "$PROJECT_DIR/.monitor.pid"
    exit 1
fi
