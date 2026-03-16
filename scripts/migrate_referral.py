#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加推广返利和余额系统
"""
import sys
import os
from pathlib import Path
from datetime import timedelta

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from app.db import DATABASE_URL

def migrate():
    """执行数据库迁移"""
    print("🔧 开始数据库迁移 - 推广返利和余额系统...")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # 1. 创建推广链接表
        if 'referral_links' not in tables:
            print("📝 创建 referral_links 表...")
            conn.execute(text("""
                CREATE TABLE referral_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username VARCHAR(50) NOT NULL,
                    referral_code VARCHAR(20) UNIQUE NOT NULL,
                    referral_url VARCHAR(500) NOT NULL,
                    total_clicks INTEGER DEFAULT 0,
                    total_registrations INTEGER DEFAULT 0,
                    total_purchases INTEGER DEFAULT 0,
                    total_earnings FLOAT DEFAULT 0.0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX idx_referral_code ON referral_links(referral_code)"))
            conn.execute(text("CREATE INDEX idx_user_id ON referral_links(user_id)"))
            conn.commit()
            print("✅ referral_links 表创建完成")
        else:
            print("✅ referral_links 表已存在")
        
        # 2. 创建推广记录表
        if 'referral_records' not in tables:
            print("📝 创建 referral_records 表...")
            conn.execute(text("""
                CREATE TABLE referral_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referral_link_id INTEGER NOT NULL,
                    referrer_id INTEGER NOT NULL,
                    referrer_username VARCHAR(50) NOT NULL,
                    referred_user_id INTEGER,
                    referred_username VARCHAR(50),
                    order_no VARCHAR(50),
                    order_amount FLOAT DEFAULT 0.0,
                    commission_rate FLOAT DEFAULT 0.3,
                    commission_amount FLOAT DEFAULT 0.0,
                    status VARCHAR(20) DEFAULT 'pending',
                    registered_at DATETIME,
                    purchased_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referral_link_id) REFERENCES referral_links(id)
                )
            """))
            conn.execute(text("CREATE INDEX idx_referrer_id ON referral_records(referrer_id)"))
            conn.execute(text("CREATE INDEX idx_referred_user_id ON referral_records(referred_user_id)"))
            conn.commit()
            print("✅ referral_records 表创建完成")
        else:
            print("✅ referral_records 表已存在")
        
        # 3. 创建用户余额表
        if 'user_balances' not in tables:
            print("📝 创建 user_balances 表...")
            conn.execute(text("""
                CREATE TABLE user_balances (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE NOT NULL,
                    username VARCHAR(50) NOT NULL,
                    balance FLOAT DEFAULT 0.0,
                    frozen_balance FLOAT DEFAULT 0.0,
                    total_recharge FLOAT DEFAULT 0.0,
                    total_consumption FLOAT DEFAULT 0.0,
                    total_commission FLOAT DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_user_balances_user_id ON user_balances(user_id)"))
            conn.commit()
            print("✅ user_balances 表创建完成")
        else:
            print("✅ user_balances 表已存在")
        
        # 4. 创建余额交易记录表
        if 'balance_transactions' not in tables:
            print("📝 创建 balance_transactions 表...")
            conn.execute(text("""
                CREATE TABLE balance_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    transaction_type VARCHAR(20) NOT NULL,
                    amount FLOAT NOT NULL,
                    balance_before FLOAT NOT NULL,
                    balance_after FLOAT NOT NULL,
                    related_order_no VARCHAR(50),
                    related_referral_id INTEGER,
                    description VARCHAR(500) DEFAULT '',
                    remark TEXT DEFAULT '',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.execute(text("CREATE INDEX idx_balance_transactions_user_id ON balance_transactions(user_id)"))
            conn.execute(text("CREATE INDEX idx_created_at ON balance_transactions(created_at)"))
            conn.commit()
            print("✅ balance_transactions 表创建完成")
        else:
            print("✅ balance_transactions 表已存在")
        
        # 5. 创建充值订单表
        if 'recharge_orders' not in tables:
            print("📝 创建 recharge_orders 表...")
            conn.execute(text("""
                CREATE TABLE recharge_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_no VARCHAR(50) UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    username VARCHAR(50) NOT NULL,
                    amount FLOAT NOT NULL,
                    payment_method VARCHAR(20) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    transaction_id VARCHAR(100),
                    paid_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expire_at DATETIME
                )
            """))
            conn.execute(text("CREATE INDEX idx_recharge_order_no ON recharge_orders(order_no)"))
            conn.commit()
            print("✅ recharge_orders 表创建完成")
        else:
            print("✅ recharge_orders 表已存在")
    
    print("\n🎉 推广返利和余额系统数据库迁移完成！")
    print("\n📋 新增功能:")
    print("  ✅ 推广链接管理")
    print("  ✅ 30% 返利系统")
    print("  ✅ 用户余额账户")
    print("  ✅ 余额充值（含赠送）")
    print("  ✅ 余额支付会员")
    print("  ✅ 交易记录追踪")
    print("\n💰 充值赠送套餐:")
    print("  • 充 30 送 2")
    print("  • 充 50 送 5")
    print("  • 充 100 送 15")
    print("  • 充 200 送 40")
    print("  • 充 500 送 120")

if __name__ == "__main__":
    migrate()
