#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加会员等级系统
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
    print("🔧 开始数据库迁移...")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        
        # 检查 users 表是否存在
        if "users" not in inspector.get_table_names():
            print("❌ users 表不存在，请先运行基础初始化")
            return
        
        # 获取 users 表的现有列
        existing_columns = [col["name"] for col in inspector.get_columns("users")]
        
        # 需要添加的列
        columns_to_add = []
        
        if "membership_level" not in existing_columns:
            columns_to_add.append("ALTER TABLE users ADD COLUMN membership_level VARCHAR(20) DEFAULT 'normal'")
        
        if "membership_expire_at" not in existing_columns:
            columns_to_add.append("ALTER TABLE users ADD COLUMN membership_expire_at DATETIME")
        
        if "total_api_calls" not in existing_columns:
            columns_to_add.append("ALTER TABLE users ADD COLUMN total_api_calls INTEGER DEFAULT 0")
        
        if "today_api_calls" not in existing_columns:
            columns_to_add.append("ALTER TABLE users ADD COLUMN today_api_calls INTEGER DEFAULT 0")
        
        if "last_api_call_at" not in existing_columns:
            columns_to_add.append("ALTER TABLE users ADD COLUMN last_api_call_at DATETIME")
        
        if "permissions" not in existing_columns:
            columns_to_add.append("ALTER TABLE users ADD COLUMN permissions JSON")
        
        if "last_login_at" not in existing_columns:
            columns_to_add.append("ALTER TABLE users ADD COLUMN last_login_at DATETIME")
        
        if "phone" not in existing_columns:
            columns_to_add.append("ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT ''")
        
        # 执行迁移
        if columns_to_add:
            print(f"📝 需要添加 {len(columns_to_add)} 个新列")
            for sql in columns_to_add:
                print(f"  → {sql}")
                conn.execute(text(sql))
                conn.commit()
            print("✅ 列添加完成")
        else:
            print("✅ 所有列已存在，无需迁移")
        
        # 创建新表
        tables_to_create = []
        
        if "api_logs" not in inspector.get_table_names():
            tables_to_create.append("""
                CREATE TABLE IF NOT EXISTS api_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    endpoint VARCHAR(200),
                    method VARCHAR(10),
                    status_code INTEGER,
                    ip_address VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        if "admin_operation_logs" not in inspector.get_table_names():
            tables_to_create.append("""
                CREATE TABLE IF NOT EXISTS admin_operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    admin_id INTEGER,
                    admin_username VARCHAR(50),
                    operation VARCHAR(100),
                    target_user_id INTEGER,
                    target_username VARCHAR(50),
                    details JSON,
                    ip_address VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
        
        if tables_to_create:
            print(f"📝 需要创建 {len(tables_to_create)} 个新表")
            for sql in tables_to_create:
                print(f"  → 创建表")
                conn.execute(text(sql))
                conn.commit()
            print("✅ 表创建完成")
        else:
            print("✅ 所有表已存在")
        
        # 更新现有用户的会员等级（如果有）
        result = conn.execute(text("SELECT COUNT(*) FROM users WHERE membership_level IS NULL OR membership_level = ''")).fetchone()
        if result[0] > 0:
            print(f"📝 更新 {result[0]} 个现有用户的会员等级...")
            conn.execute(text("UPDATE users SET membership_level = 'vip', membership_expire_at = datetime('now', '+1 day') WHERE membership_level IS NULL OR membership_level = ''"))
            conn.commit()
            print("✅ 现有用户已升级为 VIP（1 天试用）")
    
    print("🎉 数据库迁移完成！")

if __name__ == "__main__":
    migrate()
