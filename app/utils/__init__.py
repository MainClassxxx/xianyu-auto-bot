"""
数据库初始化
"""
from loguru import logger
import os

def init_db():
    """初始化数据库"""
    # 确保数据目录存在
    os.makedirs("data", exist_ok=True)
    
    # 这里初始化 SQLite 数据库
    # 创建表结构等
    
    logger.info("数据库初始化完成")
