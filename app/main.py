"""
闲鱼自动售货机器人 - 主应用入口
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from app.api import router
from app.services import scheduler
from app.utils import init_db

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("data/bot.log", rotation="10 MB", retention="7 days", level="DEBUG")

# 创建 FastAPI 应用
app = FastAPI(
    title="闲鱼自动售货机器人",
    description="支持自动发货、电影票检测、自动改价、自动买票",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    logger.info("🚀 闲鱼自动售货机器人启动中...")
    
    # 初始化数据库
    init_db()
    logger.info("✅ 数据库初始化完成")
    
    # 启动定时任务
    scheduler.start()
    logger.info("✅ 定时任务启动完成")
    
    logger.info("🎉 服务启动成功！访问 http://localhost:8080/docs 查看 API 文档")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    logger.info("👋 正在关闭服务...")
    scheduler.shutdown()

@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "闲鱼自动售货机器人",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
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
