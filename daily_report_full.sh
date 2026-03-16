#!/bin/bash

# 闲鱼每日汇报脚本 - 由 at 命令调度在早上 8:00 执行
# 执行位置：/Users/macxiaoli/.openclaw/workspace/xianyu-auto-bot

LOG_FILE="/tmp/xianyu_daily_report_$(date +\%Y\%m\%d).log"
REPORT_FILE="/tmp/xianyu_daily_report_$(date +\%Y\%m\%d).txt"

echo "=== 脚本开始执行：$(date) ===" > "$LOG_FILE"

cd /Users/macxiaoli/.openclaw/workspace/xianyu-auto-bot

echo "当前目录：$(pwd)" >> "$LOG_FILE"
echo "Git 状态：$(git status --short 2>&1 | head -5)" >> "$LOG_FILE"

# 获取昨天的 git 提交
echo "获取 git 提交..." >> "$LOG_FILE"
GIT_LOG=$(git log --since "yesterday 00:00:00" --until "yesterday 23:59:59" --oneline 2>&1)

echo "Git log 结果：" >> "$LOG_FILE"
echo "$GIT_LOG" >> "$LOG_FILE"

# 生成日报消息
if [ -z "$GIT_LOG" ] || [ "$GIT_LOG" = "" ]; then
    REPORT="📊 昨日日报（无提交）

昨天没有新的 git 提交。"
else
    REPORT="📊 昨日日报

以下是昨天的 git 提交：

$GIT_LOG"
fi

# 保存报告到文件
echo "$REPORT" > "$REPORT_FILE"
echo "报告已保存到：$REPORT_FILE" >> "$LOG_FILE"

# 尝试使用 openclaw 发送飞书消息
echo "尝试发送飞书消息..." >> "$LOG_FILE"

# 方法 1：尝试使用 openclaw agent 命令
cd /Users/macxiaoli/.openclaw/workspace
echo "执行 openclaw agent 命令..." >> "$LOG_FILE"

# 创建一个临时的指令文件
INSTRUCTION_FILE="/tmp/xianyu_send_instruction_$(date +\%Y\%m\%d).txt"
cat > "$INSTRUCTION_FILE" << EOF
请发送飞书消息给用户 ou_4e9137ec36d41793540a359e3ed2c6a6：

$REPORT
EOF

echo "指令文件已创建：$INSTRUCTION_FILE" >> "$LOG_FILE"

# 尝试执行 openclaw agent（可能需要交互式环境）
# 注意：这可能在 at 命令的非交互式环境中失败
openclaw agent --message "请读取 $INSTRUCTION_FILE 并发送飞书消息" >> "$LOG_FILE" 2>&1 || echo "openclaw agent 执行失败（可能需要交互式环境）" >> "$LOG_FILE"

echo "=== 脚本执行完成：$(date) ===" >> "$LOG_FILE"
echo "报告文件：$REPORT_FILE" >> "$LOG_FILE"
echo "日志文件：$LOG_FILE" >> "$LOG_FILE"

# 输出到标准输出（at 命令会邮件通知）
echo "每日汇报脚本执行完成"
echo "报告文件：$REPORT_FILE"
echo "日志文件：$LOG_FILE"
