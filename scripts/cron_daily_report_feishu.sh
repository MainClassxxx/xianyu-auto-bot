#!/bin/bash
# 闲鱼机器人每日汇报 - 飞书版本
# 每天早上 8 点执行，通过 OpenClaw 发送到当前飞书对话

set -e

PROJECT_DIR="/Users/macxiaoli/.openclaw/workspace/xianyu-auto-bot"
SCRIPT_DIR="/Users/macxiaoli/.openclaw/workspace/xianyu-auto-bot/scripts"
REPORT_FILE="/tmp/xianyu_daily_report_$(date -v-1d +%Y-%m-%d).txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始生成每日汇报..."

# 生成日报
cd "$PROJECT_DIR"
python3 "$SCRIPT_DIR/daily_report_feishu.py" > "$REPORT_FILE"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 日报已生成：$REPORT_FILE"

# 读取日报内容
REPORT_CONTENT=$(cat "$REPORT_FILE")

# 将日报写入临时文件供 OpenClaw 读取
echo "$REPORT_CONTENT" > /tmp/xianyu_report_to_send.txt

# 使用 osascript 触发通知，提醒用户查看
osascript -e "display notification \"闲鱼机器人日报已生成\" with title \"易拉罐 🥫\""

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 每日汇报完成 - 报告内容在 /tmp/xianyu_report_to_send.txt"
