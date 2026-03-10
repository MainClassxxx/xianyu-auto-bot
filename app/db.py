"""
数据库配置和初始化
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from loguru import logger
import os

# 数据库 URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/xianyu_bot.db")

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite 需要
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

def init_db():
    """初始化数据库，创建所有表"""
    from app.models import Account, Item, Order, Message, AutoReplyRule, DeliveryRule, NotificationChannel, SystemLog
    
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    logger.info("✅ 数据库初始化完成")
    logger.info(f"📁 数据库路径：{DATABASE_URL}")

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
