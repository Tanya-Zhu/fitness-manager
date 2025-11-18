#!/bin/bash

# 停止监控服务

PROJECT_DIR="/Users/admin/my-project"
cd "$PROJECT_DIR"

echo "🛑 停止监控服务..."

# 从PID文件停止
if [ -f "$PROJECT_DIR/.monitor.pid" ]; then
    MONITOR_PID=$(cat "$PROJECT_DIR/.monitor.pid")
    if ps -p $MONITOR_PID > /dev/null 2>&1; then
        kill $MONITOR_PID
        sleep 1
        if ps -p $MONITOR_PID > /dev/null 2>&1; then
            kill -9 $MONITOR_PID
        fi
        echo "✅ 监控服务已停止 (PID: $MONITOR_PID)"
    else
        echo "⚠️  监控进程不存在 (PID: $MONITOR_PID)"
    fi
    rm -f "$PROJECT_DIR/.monitor.pid"
fi

# 清理其他可能的监控进程
OTHER_MONITORS=$(ps aux | grep "bash.*monitor.sh" | grep -v grep | awk '{print $2}')
if [ ! -z "$OTHER_MONITORS" ]; then
    echo "🔍 发现其他监控进程，正在清理..."
    echo "$OTHER_MONITORS" | xargs kill 2>/dev/null
    echo "✅ 已清理所有监控进程"
fi

echo "✅ 监控服务已完全停止"
