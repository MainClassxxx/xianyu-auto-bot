"""
定时任务调度器
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from datetime import datetime

scheduler = AsyncIOScheduler()

async def check_orders_job():
    """订单检查任务 - 每 5 分钟"""
    try:
        logger.info("⏰ 执行订单检查任务...")
        
        from app.db import SessionLocal
        from app.services.xianyu_api import xianyu_manager
        from app.services.auto_delivery_service import AutoDeliveryService
        from app.models import Account
        
        db = SessionLocal()
        
        # 获取所有活跃账号
        accounts = db.query(Account).filter(Account.status == "active").all()
        
        for account in accounts:
            client = xianyu_manager.get_client(str(account.id))
            if client:
                delivery_service = AutoDeliveryService(db)
                count = await delivery_service.check_and_deliver(account.id, client)
                if count > 0:
                    logger.info(f"✅ 账号 {account.name} 自动发货 {count} 单")
        
        db.close()
        
    except Exception as e:
        logger.error(f"❌ 订单检查任务失败：{e}")

async def update_prices_job():
    """自动改价任务 - 每 30 分钟"""
    try:
        logger.info("⏰ 执行自动改价任务...")
        # TODO: 实现自动改价逻辑
    except Exception as e:
        logger.error(f"❌ 自动改价任务失败：{e}")

async def cleanup_job():
    """清理任务 - 每天凌晨 3 点"""
    try:
        logger.info("⏰ 执行清理任务...")
        # TODO: 清理过期数据
    except Exception as e:
        logger.error(f"❌ 清理任务失败：{e}")

def start_scheduler():
    """启动调度器"""
    # 订单检查 - 每 5 分钟
    scheduler.add_job(
        check_orders_job,
        'interval',
        minutes=5,
        id='check_orders',
        name='检查订单'
    )
    
    # 自动改价 - 每 30 分钟
    scheduler.add_job(
        update_prices_job,
        'interval',
        minutes=30,
        id='update_prices',
        name='自动改价'
    )
    
    # 清理任务 - 每天凌晨 3 点
    scheduler.add_job(
        cleanup_job,
        CronTrigger(hour=3, minute=0),
        id='cleanup',
        name='清理数据'
    )
    
    scheduler.start()
    logger.info("✅ 定时任务调度器已启动")

def shutdown_scheduler():
    """关闭调度器"""
    scheduler.shutdown()
    logger.info("👋 定时任务调度器已关闭")
