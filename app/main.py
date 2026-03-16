"""
闲鱼自动售货机器人 - 主应用入口 v3.0
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from loguru import logger
import sys
import os

# 设置项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("data/bot.log", rotation="10 MB", retention="7 days", level="DEBUG")

# 创建 FastAPI 应用
app = FastAPI(
    title="闲鱼自动售货机器人 v3.0",
    description="完整的闲鱼自动化管理工具 - 真实 API 连接",
    version="3.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("🚀 闲鱼自动售货机器人 v3.0 启动中...")
    
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 初始化数据库
    from app.db import init_db
    init_db()
    logger.info("✅ 数据库初始化完成")
    
    # 启动定时任务
    from app.services.scheduler import start_scheduler
    start_scheduler()
    logger.info("✅ 定时任务启动完成")
    
    # 启动每小时飞书汇报（需要配置 Webhook）
    try:
        from app.services.hourly_report import start_hourly_report
        start_hourly_report()
        logger.info("✅ 每小时飞书汇报已启动")
    except Exception as e:
        logger.warning(f"⚠️ 飞书汇报启动失败：{e}")
    
    logger.info("🎉 服务启动成功！")
    logger.info("📖 API 文档：http://localhost:8080/docs")
    logger.info("📊 健康检查：http://localhost:8080/health")
    logger.info("🎨 前端界面：http://localhost:3000")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("👋 正在关闭服务...")
    
    # 关闭闲鱼客户端
    from app.services.xianyu_api import xianyu_manager
    await xianyu_manager.close_all()
    
    # 关闭定时任务
    from app.services.scheduler import shutdown_scheduler
    shutdown_scheduler()

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "闲鱼自动售货机器人",
        "version": "3.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

# 导入并注册所有 API 路由
from app.api import accounts, items, orders, conversations, auto_reply, auto_delivery, notifications, stats, auth, admin

app.include_router(accounts.router)
app.include_router(items.router)
app.include_router(orders.router)
app.include_router(conversations.router)
app.include_router(auto_reply.router)
app.include_router(auto_delivery.router)
app.include_router(notifications.router)
app.include_router(stats.router)
app.include_router(auth.router)
app.include_router(admin.router)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
