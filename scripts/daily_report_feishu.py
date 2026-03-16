#!/usr/bin/env python3
"""
闲鱼机器人每日汇报脚本
生成昨日开发日报并通过 OpenClaw 发送到飞书
"""
import subprocess
import json
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
        return []

def get_recent_commits():
    """获取最近 5 次提交"""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split("\n") if result.stdout.strip() else []
    except Exception as e:
        return []

def get_project_stats():
    """获取项目统计信息"""
    try:
        # 获取文件数量
        result = subprocess.run(
            ["find", ".", "-type", "f", "-not", "-path", "./.git/*", "-not", "-path", "./node_modules/*"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        file_count = len(result.stdout.strip().split("\n"))
        
        # 获取代码行数
        result = subprocess.run(
            ["find", ".", "-name", "*.py", "-o", "-name", "*.js", "-o", "-name", "*.ts", "-o", "-name", "*.vue"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )
        code_files = result.stdout.strip().split("\n")
        total_lines = 0
        for f in code_files:
            if f and Path(f).exists():
                try:
                    with open(f, 'r', encoding='utf-8', errors='ignore') as file:
                        total_lines += len(file.readlines())
                except:
                    pass
        
        return file_count, total_lines
    except Exception as e:
        return 0, 0

def generate_daily_report():
    """生成日报内容"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    weekday = datetime.now().strftime("%A")
    
    commits = get_yesterday_commits()
    recent_commits = get_recent_commits()
    file_count, total_lines = get_project_stats()
    
    # 构建日报消息
    report = f"""📅 **闲鱼机器人开发日报**

**日期**: {yesterday}
**汇报时间**: {today} {datetime.now().strftime("%H:%M")}
**星期**: {weekday}

━━━━━━━━━━━━━━━━━━━━

✅ **昨日完成**

"""
    
    if commits and commits[0]:
        for commit in commits[:10]:
            report += f"• {commit}\n"
    else:
        report += "• 昨日无新提交\n"
    
    report += f"""
📊 **项目统计**

• 文件总数：{file_count} 个
• 代码行数：约 {total_lines} 行

📋 **今日计划**

1. 完善闲鱼 API 客户端
2. 实现自动发货调度器
3. 集成飞书通知
4. 修复发现的问题

🔗 **仓库链接**
https://github.com/MainClassxxx/xianyu-auto-bot

━━━━━━━━━━━━━━━━━━━━

**汇报人**: 易拉罐 🥫
"""
    
    return report

if __name__ == "__main__":
    report = generate_daily_report()
    print(report)
