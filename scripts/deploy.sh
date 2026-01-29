#!/bin/bash
# 服务器端手动部署脚本
# 用法: ./scripts/deploy.sh

set -e

echo "Starting deployment..."

# 拉取最新代码
echo "Pulling latest code..."
git pull origin main

# 同步依赖
echo "Syncing dependencies with uv..."
uv sync

# 重启服务
echo "Restarting bot service..."

# 查找并停止旧进程
pkill -f "python -m bot" || true
sleep 2

# 启动新进程 (后台运行)
nohup uv run python -m bot > bot.log 2>&1 &

echo "Deployment completed successfully!"
echo "Bot is running in background."
echo "Check logs with: tail -f bot.log"
