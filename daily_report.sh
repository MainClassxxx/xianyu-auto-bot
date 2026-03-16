#!/bin/bash

# 每日汇报脚本 - 早上 8 点执行
# 此脚本由 at 命令调度执行

cd /Users/macxiaoli/.openclaw/workspace/xianyu-auto-bot

# 获取昨天的 git 提交
GIT_LOG=$(git log --since "yesterday 00:00:00" --until "yesterday 23:59:59" --oneline 2>&1)

# 生成日报消息
if [ -z "$GIT_LOG" ] || [ "$GIT_LOG" = "" ]; then
    REPORT="📊 昨日日报（无提交）

昨天没有新的 git 提交。"
else
    REPORT="📊 昨日日报

以下是昨天的 git 提交：

$GIT_LOG"
fi

# 将报告写入临时文件
echo "$REPORT" > /tmp/xianyu_daily_report.txt

# 使用 openclaw agent 发送消息
# 通过创建一个临时的 agent 请求来发送消息
cat > /tmp/send_report_request.json << EOF
{
  "action": "send",
  "channel": "feishu",
  "target": "ou_4e9137ec36d41793540a359e3ed2c6a6",
  "message": "$REPORT"
}
EOF

# 尝试使用 openclaw agent 发送消息
# 注意：这可能需要正确的环境和权限
cd /Users/macxiaoli/.openclaw/workspace
openclaw agent --message "请发送飞书消息：$(cat /tmp/xianyu_daily_report.txt)" 2>&1 | tee /tmp/xianyu_report_log.txt

echo "脚本执行完成时间：$(date)" >> /tmp/xianyu_report_log.txt
