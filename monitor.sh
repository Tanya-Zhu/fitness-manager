#!/bin/bash

# 运动管家 - 隧道监控和自动重启脚本
# 每分钟检查一次隧道状态，如果断开则自动重启

PROJECT_DIR="/Users/admin/my-project"
cd "$PROJECT_DIR"

LOG_FILE="$PROJECT_DIR/monitor.log"
MAX_FAILURES=3  # 连续失败3次才重启

echo "========================================" >> "$LOG_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') - 监控脚本启动" >> "$LOG_FILE"

failure_count=0

while true; do
    # 检查隧道进程是否存在
    if [ -f "$PROJECT_DIR/.tunnel.pid" ]; then
        TUNNEL_PID=$(cat "$PROJECT_DIR/.tunnel.pid")

        if ! ps -p $TUNNEL_PID > /dev/null 2>&1; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') - ⚠️  隧道进程不存在，准备重启..." >> "$LOG_FILE"
            "$PROJECT_DIR/stop.sh" >> "$LOG_FILE" 2>&1
            sleep 3
            "$PROJECT_DIR/start-background.sh" >> "$LOG_FILE" 2>&1
            failure_count=0
            sleep 30  # 重启后等待30秒再继续监控
            continue
        fi
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S') - ⚠️  未找到隧道PID文件，准备重启..." >> "$LOG_FILE"
        "$PROJECT_DIR/stop.sh" >> "$LOG_FILE" 2>&1
        sleep 3
        "$PROJECT_DIR/start-background.sh" >> "$LOG_FILE" 2>&1
        failure_count=0
        sleep 30
        continue
    fi

    # 检查隧道是否可访问
    if [ -f "$PROJECT_DIR/.tunnel_url" ]; then
        TUNNEL_URL=$(cat "$PROJECT_DIR/.tunnel_url")

        # 测试URL是否可访问
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$TUNNEL_URL" 2>/dev/null)

        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "302" ] || [ "$HTTP_CODE" = "301" ]; then
            # 隧道正常
            if [ $failure_count -gt 0 ]; then
                echo "$(date '+%Y-%m-%d %H:%M:%S') - ✅ 隧道恢复正常 (HTTP $HTTP_CODE)" >> "$LOG_FILE"
            fi
            failure_count=0
        else
            # 隧道异常
            failure_count=$((failure_count + 1))
            echo "$(date '+%Y-%m-%d %H:%M:%S') - ⚠️  隧道访问异常 (HTTP $HTTP_CODE) - 失败计数: $failure_count/$MAX_FAILURES" >> "$LOG_FILE"

            # 连续失败达到阈值，重启服务
            if [ $failure_count -ge $MAX_FAILURES ]; then
                echo "$(date '+%Y-%m-%d %H:%M:%S') - 🔄 连续失败 $MAX_FAILURES 次，开始重启服务..." >> "$LOG_FILE"
                "$PROJECT_DIR/stop.sh" >> "$LOG_FILE" 2>&1
                sleep 3
                "$PROJECT_DIR/start-background.sh" >> "$LOG_FILE" 2>&1
                failure_count=0
                sleep 30  # 重启后等待30秒
                continue
            fi
        fi
    fi

    # 每分钟检查一次
    sleep 60
done
