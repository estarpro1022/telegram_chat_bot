#!/bin/bash
# 服务器端重启脚本
# 用法: ./scripts/restart.sh

set -e

# ==========================================
# 环境配置 (Environment Setup)
# ==========================================
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$APP_DIR/bot.pid"
LOG_FILE="$APP_DIR/bot.log"

# ==========================================
# 停止旧进程 (Stop Old Process)
# ==========================================
echo "🛑 Checking for running process..."
if [ -f "$PID_FILE" ]; then
    OLD_PID="$(cat "$PID_FILE" || true)"
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" >/dev/null 2>&1; then
        echo "Stopping old process: $OLD_PID"
        kill "$OLD_PID" || true

        # 最多等 10 秒让进程优雅退出
        for i in $(seq 1 10); do
            if kill -0 "$OLD_PID" >/dev/null 2>&1; then
                sleep 1
            else
                break
            fi
        done

        # 若还活着就强杀
        if kill -0 "$OLD_PID" >/dev/null 2>&1; then
            echo "Force killing $OLD_PID"
            kill -9 "$OLD_PID" || true
        fi
    fi
    rm -f "$PID_FILE"
else
    echo "No PID file found. Skipping stop."
fi

# ==========================================
# 启动新进程 (Start New Process)
# ==========================================
echo "✅ Starting new bot process..."
cd "$APP_DIR"
nohup uv run python -m bot > "$LOG_FILE" 2>&1 &
NEW_PID=$!
echo "$NEW_PID" > "$PID_FILE"

echo "🎉 Bot started successfully with PID: $NEW_PID"
echo "📄 Logs are being written to: $LOG_FILE"
echo "🔍 Check logs with: tail -f $LOG_FILE"
