#!/usr/bin/env python3
"""
数据库迁移脚本 - 完善自动发货系统
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
    print("🔧 开始数据库迁移 - 自动发货系统...")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        # 1. 创建发货规则表
        if 'delivery_rules' not in tables:
            print("📝 创建 delivery_rules 表...")
            conn.execute(text("""
                CREATE TABLE delivery_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    keyword VARCHAR(200),
                    match_type VARCHAR(20) DEFAULT 'contains',
                    delivery_content TEXT NOT NULL,
                    delivery_type VARCHAR(20) DEFAULT 'text',
                    stock INTEGER DEFAULT -1,
                    auto_restock BOOLEAN DEFAULT 0,
                    enabled BOOLEAN DEFAULT 1,
                    priority INTEGER DEFAULT 0,
                    total_delivered INTEGER DEFAULT 0,
                    today_delivered INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                )
            """))
            conn.execute(text("CREATE INDEX idx_account_id ON delivery_rules(account_id)"))
            conn.execute(text("CREATE INDEX idx_enabled ON delivery_rules(enabled)"))
            conn.commit()
            print("✅ delivery_rules 表创建完成")
        else:
            print("✅ delivery_rules 表已存在")
        
        # 2. 创建发货记录表
        if 'delivery_records' not in tables:
            print("📝 创建 delivery_records 表...")
            conn.execute(text("""
                CREATE TABLE delivery_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    rule_id INTEGER,
                    order_id VARCHAR(50) NOT NULL,
                    order_no VARCHAR(50),
                    item_title VARCHAR(500),
                    buyer_name VARCHAR(100),
                    delivery_content TEXT,
                    delivery_type VARCHAR(20),
                    delivery_status VARCHAR(20) DEFAULT 'pending',
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    delivered_at DATETIME,
                    FOREIGN KEY (account_id) REFERENCES accounts(id),
                    FOREIGN KEY (rule_id) REFERENCES delivery_rules(id)
                )
            """))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_order_id ON delivery_records(order_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_account_id ON delivery_records(account_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_created_at ON delivery_records(created_at)"))
            conn.commit()
            print("✅ delivery_records 表创建完成")
        else:
            print("✅ delivery_records 表已存在")
        
        # 3. 创建自动发货日志表
        if 'auto_delivery_logs' not in tables:
            print("📝 创建 auto_delivery_logs 表...")
            conn.execute(text("""
                CREATE TABLE auto_delivery_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER NOT NULL,
                    level VARCHAR(20) DEFAULT 'INFO',
                    action VARCHAR(50),
                    message TEXT,
                    order_id VARCHAR(50),
                    rule_id INTEGER,
                    data JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_id) REFERENCES accounts(id)
                )
            """))
            conn.execute(text("CREATE INDEX idx_account_id ON auto_delivery_logs(account_id)"))
            conn.execute(text("CREATE INDEX idx_created_at ON auto_delivery_logs(created_at)"))
            conn.commit()
            print("✅ auto_delivery_logs 表创建完成")
        else:
            print("✅ auto_delivery_logs 表已存在")
        
        # 4. 检查 accounts 表是否存在
        if 'accounts' not in tables:
            print("⚠️ accounts 表不存在，创建基础账号表...")
            conn.execute(text("""
                CREATE TABLE accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    cookie TEXT NOT NULL,
                    device_id VARCHAR(50),
                    status VARCHAR(20) DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """))
            conn.commit()
            print("✅ accounts 表创建完成")
        else:
            print("✅ accounts 表已存在")
    
    print("\n🎉 自动发货系统数据库迁移完成！")
    print("\n📋 新增功能:")
    print("  ✅ 发货规则管理（关键词匹配、库存管理）")
    print("  ✅ 发货记录追踪（成功/失败记录）")
    print("  ✅ 自动发货日志（操作日志、错误日志）")
    print("  ✅ 账号管理表（闲鱼账号 Cookie 管理）")
    print("\n🔄 自动发货流程:")
    print("  1. 定时轮询已付款订单")
    print("  2. 匹配发货规则（关键词）")
    print("  3. 检查库存（如有限制）")
    print("  4. 自动发货（发送消息给买家）")
    print("  5. 记录发货日志")
    print("  6. 扣减库存")

if __name__ == "__main__":
    migrate()
