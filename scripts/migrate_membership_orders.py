#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加会员订单系统
"""
import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from app.db import DATABASE_URL

def migrate():
    """执行数据库迁移"""
    print("🔧 开始数据库迁移 - 会员订单系统...")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # 1. 创建会员订单表
        if 'membership_orders' not in tables:
            print("📝 创建 membership_orders 表...")
            conn.execute(text("""
                CREATE TABLE membership_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_no VARCHAR(50) UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    username VARCHAR(50) NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    plan VARCHAR(50) NOT NULL,
                    days INTEGER NOT NULL,
                    price FLOAT NOT NULL,
                    payment_method VARCHAR(20),
                    transaction_id VARCHAR(100),
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    paid_at DATETIME,
                    expire_at DATETIME,
                    remark TEXT DEFAULT ''
                )
            """))
            conn.execute(text("CREATE INDEX idx_order_no ON membership_orders(order_no)"))
            conn.execute(text("CREATE INDEX idx_user_id ON membership_orders(user_id)"))
            conn.commit()
            print("✅ membership_orders 表创建完成")
        else:
            print("✅ membership_orders 表已存在")
        
        # 2. 创建会员开通日志表
        if 'membership_grant_logs' not in tables:
            print("📝 创建 membership_grant_logs 表...")
            conn.execute(text("""
                CREATE TABLE membership_grant_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER NOT NULL,
                    admin_username VARCHAR(50) NOT NULL,
                    user_id INTEGER NOT NULL,
                    username VARCHAR(50) NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    days INTEGER NOT NULL,
                    reason VARCHAR(500) DEFAULT '',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            print("✅ membership_grant_logs 表创建完成")
        else:
            print("✅ membership_grant_logs 表已存在")
        
        # 3. 更新现有用户的会员等级（如果没有设置）
        result = conn.execute(text("""
            SELECT COUNT(*) FROM users 
            WHERE membership_level IS NULL 
               OR membership_level = '' 
               OR membership_level = 'normal'
        """)).fetchone()
        
        if result[0] > 0:
            print(f"📝 更新 {result[0]} 个普通用户...")
            conn.execute(text("""
                UPDATE users 
                SET membership_level = 'vip', 
                    membership_expire_at = datetime('now', '+1 day')
                WHERE membership_level IS NULL 
                   OR membership_level = ''
                   OR membership_level = 'normal'
            """))
            conn.commit()
            print("✅ 普通用户已升级为 VIP（1 天试用）")
    
    print("\n🎉 会员订单系统数据库迁移完成！")
    print("\n📋 新增功能:")
    print("  ✅ 会员购买订单表")
    print("  ✅ 会员开通日志表")
    print("  ✅ 新用户自动升级 VIP 试用")

if __name__ == "__main__":
    migrate()
