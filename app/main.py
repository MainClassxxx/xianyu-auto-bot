"""
闲鱼自动售货机器人 - 主应用入口
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

# 导入所有 API 路由
from app.api import (
    accounts,
    items,
    orders,
    conversations,
    auto_reply,
    auto_delivery,
    notifications,
    stats
)

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("data/bot.log", rotation="10 MB", retention="7 days", level="DEBUG")

# 创建 FastAPI 应用
app = FastAPI(
    title="闲鱼自动售货机器人",
    description="完整的闲鱼自动化管理工具 - 支持多账号、自动回复、自动发货、数据统计",
    version="2.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有 API 路由
app.include_router(accounts.router)
app.include_router(items.router)
app.include_router(orders.router)
app.include_router(conversations.router)
app.include_router(auto_reply.router)
app.include_router(auto_delivery.router)
app.include_router(notifications.router)
app.include_router(stats.router)

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("🚀 闲鱼自动售货机器人 v2.0 启动中...")
    
    # TODO: 初始化数据库
    # TODO: 加载配置
    # TODO: 启动定时任务
    # TODO: 连接闲鱼账号
    
    logger.info("✅ 服务启动成功！")
    logger.info("📖 API 文档：http://localhost:8080/docs")
    logger.info("📊 健康检查：http://localhost:8080/health")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("👋 正在关闭服务...")
    # TODO: 关闭数据库连接
    # TODO: 断开闲鱼连接

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "闲鱼自动售货机器人",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
