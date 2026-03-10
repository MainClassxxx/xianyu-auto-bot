"""
定时进度汇报 - 每小时发送飞书消息
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from datetime import datetime
import httpx

# 飞书 Webhook（需要啤酒瓶配置）
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_HERE"

# 进度追踪
progress_data = {
    "day": 1,
    "total_tasks": 93,
    "completed_tasks": 5,
    "current_task": "开发登录注册前端页面",
    "start_date": "2026-03-10",
    "target_date": "2026-03-17"
}

async def send_feishu_report():
    """发送飞书进度报告"""
    try:
        # 计算进度
        progress_percent = (progress_data["completed_tasks"] / progress_data["total_tasks"]) * 100
        
        # 构建消息内容
        content = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": f"🚀 闲鱼机器人开发进度 - Day {progress_data['day']}"
                    },
                    "template": "blue"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**当前进度**: {progress_percent:.1f}% ({progress_data['completed_tasks']}/{progress_data['total_tasks']})"
                        }
                    },
                    {
                        "tag": "progress",
                        "value": int(progress_percent),
                        "color": "blue"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"**当前任务**: {progress_data['current_task']}"
                        }
                    },
                    {
                        "tag": "hr"
                    },
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": f"📅 开始日期：{progress_data['start_date']}\n🎯 目标日期：{progress_data['target_date']}\n⏰ 汇报时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        }
                    },
                    {
                        "tag": "action",
                        "actions": [
                            {
                                "tag": "button",
                                "text": {
                                    "tag": "plain_text",
                                    "content": "查看项目"
                                },
                                "url": "https://github.com/MainClassxxx/xianyu-auto-bot",
                                "type": "primary"
                            }
                        ]
                    }
                ]
            }
        }
        
        # 发送消息
        async with httpx.AsyncClient() as client:
            response = await client.post(FEISHU_WEBHOOK, json=content, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ 飞书进度报告已发送")
            else:
                logger.error(f"❌ 飞书发送失败：{response.text}")
                
    except Exception as e:
        logger.error(f"❌ 发送飞书报告失败：{e}")

def start_hourly_report():
    """启动每小时汇报"""
    scheduler = AsyncIOScheduler()
    
    # 每小时整点发送
    scheduler.add_job(
        send_feishu_report,
        CronTrigger(minute=0),
        id='hourly_report',
        name='每小时进度汇报'
    )
    
    scheduler.start()
    logger.info("✅ 每小时飞书汇报已启动")
    
    return scheduler

def update_progress(completed: int, current_task: str, day: int = None):
    """更新进度"""
    progress_data["completed_tasks"] = completed
    progress_data["current_task"] = current_task
    if day:
        progress_data["day"] = day
    
    logger.info(f"📊 进度更新：{completed}/{progress_data['total_tasks']} - {current_task}")
