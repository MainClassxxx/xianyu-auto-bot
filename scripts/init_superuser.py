"""
超级管理员初始化脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db, SessionLocal
from app.models.user import User
from app.models import Account
from passlib.context import CryptContext
from loguru import logger
import hashlib

# 配置日志
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

# 使用 pbkdf2 替代 bcrypt（避免版本兼容性问题）
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def init_superuser():
    """初始化超级管理员"""
    logger.info("🔧 开始初始化超级管理员...")
    
    # 初始化数据库
    init_db()
    
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        admin = db.query(User).filter(User.role == "admin").first()
        
        if admin:
            logger.info(f"✅ 超级管理员已存在：{admin.username}")
            return
        
        # 创建超级管理员
        superuser = User(
            username="admin",
            email="admin@xianyu-bot.local",
            password_hash=pwd_context.hash("admin123456"),  # 默认密码
            role="admin",
            status="active",
            agree_terms=True
        )
        
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        
        logger.info("✅ 超级管理员创建成功！")
        logger.info("📝 登录信息:")
        logger.info("   用户名：admin")
        logger.info("   密码：admin123456")
        logger.info("⚠️  请在首次登录后修改密码！")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ 初始化失败：{e}")
        raise
    finally:
        db.close()

def init_demo_account():
    """初始化测试账号（可选）"""
    logger.info("🔧 初始化测试账号...")
    
    db = SessionLocal()
    try:
        # 检查是否已有账号
        try:
            count = db.query(Account).count()
            if count > 0:
                logger.info(f"✅ 已存在 {count} 个账号，跳过初始化")
                return
        except Exception:
            # 表不存在，跳过
            pass
        
        logger.info("✅ 无需初始化测试账号")
        
    finally:
        db.close()

if __name__ == "__main__":
    init_superuser()
    init_demo_account()
    logger.info("🎉 初始化完成！")
