#!/bin/bash
# 闲鱼机器人每日汇报 - Cron 脚本
# 每天早上 8 点执行

# 项目目录
PROJECT_DIR="/Users/macxiaoli/.openclaw/workspace/xianyu-auto-bot"
REPORT_DATE=$(date -v-1d +"%Y-%m-%d")
TODAY=$(date +"%Y-%m-%d %H:%M")

# 生成日报
cd "$PROJECT_DIR"
python3 scripts/daily_report.py > "/tmp/xianyu_daily_report_${REPORT_DATE}.md"

# 通过飞书 Webhook 发送（如果配置了）
if [ -n "$FEISHU_WEBHOOK" ]; then
    curl -X POST "$FEISHU_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "$(cat <<EOF
{
    "msg_type": "text",
    "content": {
        "text": "📅 闲鱼机器人开发日报 (${REPORT_DATE})\n\n日报已生成，请查看：https://github.com/MainClassxxx/xianyu-auto-bot/blob/main/DAILY_REPORT_${REPORT_DATE}.md\n\n汇报时间：${TODAY}"
    }
}
EOF
)"
fi

echo "[$TODAY] 每日汇报已生成"
