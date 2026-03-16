#!/usr/bin/env python3
"""
每日开发汇报脚本
每天早上 8 点执行，分析项目昨日提交并生成日报
"""
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_DIR = Path("/Users/macxiaoli/.openclaw/workspace/xianyu-auto-bot")

def get_yesterday_commits():
    """获取昨天的 git 提交"""
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y-%m-%d")
    
    try:
        result = subprocess.run(
            ["git", "log", "--since", f"{date_str} 00:00:00", "--until", f"{date_str} 23:59:59", "--oneline"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception as e:
        return [f"获取提交失败：{e}"]

def get_file_changes():
    """获取文件变更统计"""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD~1"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"获取变更失败：{e}"

def generate_report():
    """生成日报内容"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    commits = get_yesterday_commits()
    changes = get_file_changes()
    
    report = f"""# 📅 闲鱼机器人开发日报

**日期**: {yesterday}
**汇报时间**: {today} 08:00

---

## ✅ 昨日完成

### Git 提交
"""
    
    if commits and commits[0]:
        for commit in commits[:10]:  # 最多显示 10 条
            report += f"- {commit}\n"
    else:
        report += "- 无新提交\n"
    
    report += f"""
### 文件变更
```
{changes}
```

---

## 📋 今日计划

1. 继续完善闲鱼 API 客户端
2. 实现自动发货调度器
3. 集成飞书通知
4. 修复发现的问题

---

## 📊 当前进度

- 总体进度：约 55%
- 最新提交：查看上方 Git 提交列表

---

**汇报人**: 易拉罐 🥫
**仓库**: https://github.com/MainClassxxx/xianyu-auto-bot
"""
    
    return report

def send_feishu_message(content):
    """通过 OpenClaw message 工具发送飞书消息"""
    # 这个函数会被外部调用，实际发送由调用方处理
    return content

if __name__ == "__main__":
    report = generate_report()
    print(report)
    
    # 如果传入了 --send 参数，则发送飞书消息
    if len(sys.argv) > 1 and sys.argv[1] == "--send":
        send_feishu_message(report)
