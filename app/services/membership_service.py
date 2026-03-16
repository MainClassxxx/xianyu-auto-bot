"""
权限管理服务
定义不同等级用户的权限和限制
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User, MembershipLevel

# 权限定义
PERMISSIONS = {
    # 基础权限
    "api.basic": "基础 API 调用",
    "api.advanced": "高级 API 调用",
    "api.auto_delivery": "自动发货",
    "api.auto_reply": "自动回复",
    "api.multi_account": "多账号管理",
    "api.data_export": "数据导出",
    "api.webhook": "Webhook 回调",
    "api.ai_reply": "AI 智能回复",
    
    # 管理权限
    "admin.users": "用户管理",
    "admin.accounts": "账号管理",
    "admin.logs": "日志查看",
    "admin.system": "系统设置",
}

# 等级权限配置
LEVEL_CONFIG = {
    MembershipLevel.NORMAL.value: {
        "name": "普通用户",
        "max_accounts": 1,           # 最多绑定账号数
        "daily_api_limit": 100,      # 每日 API 调用限制
        "permissions": [
            "api.basic",
        ],
        "features": {
            "auto_delivery": False,   # 自动发货
            "auto_reply": False,      # 自动回复
            "multi_account": False,   # 多账号管理
            "data_export": False,     # 数据导出
            "webhook": False,         # Webhook
            "ai_reply": False,        # AI 回复
        }
    },
    MembershipLevel.VIP.value: {
        "name": "VIP 用户",
        "max_accounts": 5,
        "daily_api_limit": 1000,
        "permissions": [
            "api.basic",
            "api.advanced",
            "api.auto_delivery",
            "api.auto_reply",
            "api.multi_account",
            "api.data_export",
        ],
        "features": {
            "auto_delivery": True,
            "auto_reply": True,
            "multi_account": True,
            "data_export": True,
            "webhook": False,
            "ai_reply": False,
        }
    },
    MembershipLevel.SVIP.value: {
        "name": "SVIP 用户",
        "max_accounts": -1,  # 无限制
        "daily_api_limit": -1,  # 无限制
        "permissions": [
            "api.basic",
            "api.advanced",
            "api.auto_delivery",
            "api.auto_reply",
            "api.multi_account",
            "api.data_export",
            "api.webhook",
            "api.ai_reply",
        ],
        "features": {
            "auto_delivery": True,
            "auto_reply": True,
            "multi_account": True,
            "data_export": True,
            "webhook": True,
            "ai_reply": True,
        }
    }
}

# 角色权限配置
ROLE_PERMISSIONS = {
    "user": [],
    "admin": [
        "admin.users",
        "admin.accounts",
        "admin.logs",
    ],
    "super_admin": [
        "admin.users",
        "admin.accounts",
        "admin.logs",
        "admin.system",
    ]
}

class MembershipService:
    """会员服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_level_config(self, level: str) -> Dict:
        """获取等级配置"""
        return LEVEL_CONFIG.get(level, LEVEL_CONFIG[MembershipLevel.NORMAL.value])
    
    def check_permission(self, user: User, permission: str) -> bool:
        """检查用户是否有指定权限"""
        # 检查会员等级权限
        level_config = self.get_level_config(user.membership_level)
        if permission in level_config["permissions"]:
            return True
        
        # 检查角色权限
        role_perms = ROLE_PERMISSIONS.get(user.role, [])
        if permission in role_perms:
            return True
        
        # 检查额外权限
        if user.permissions and permission in user.permissions:
            return True
        
        return False
    
    def check_feature(self, user: User, feature: str) -> bool:
        """检查用户是否可以使用指定功能"""
        level_config = self.get_level_config(user.membership_level)
        return level_config["features"].get(feature, False)
    
    def check_api_limit(self, user: User) -> tuple[bool, str]:
        """检查用户是否达到 API 调用限制"""
        # 管理员无限制
        if user.role in ["admin", "super_admin"]:
            return True, ""
        
        level_config = self.get_level_config(user.membership_level)
        daily_limit = level_config["daily_api_limit"]
        
        # -1 表示无限制
        if daily_limit == -1:
            return True, ""
        
        # 检查今日调用次数
        if user.today_api_calls >= daily_limit:
            return False, f"今日 API 调用次数已达上限 ({daily_limit}次)"
        
        return True, ""
    
    def check_account_limit(self, user: User, current_count: int) -> tuple[bool, str]:
        """检查用户是否可以添加更多账号"""
        level_config = self.get_level_config(user.membership_level)
        max_accounts = level_config["max_accounts"]
        
        # -1 表示无限制
        if max_accounts == -1:
            return True, ""
        
        if current_count >= max_accounts:
            return False, f"账号数量已达上限 ({max_accounts}个)"
        
        return True, ""
    
    def is_membership_valid(self, user: User) -> bool:
        """检查会员是否在有效期内"""
        if user.membership_level == MembershipLevel.NORMAL.value:
            return False
        
        if not user.membership_expire_at:
            return True
        
        return user.membership_expire_at > datetime.now()
    
    def upgrade_membership(self, user: User, level: str, days: int = 30) -> User:
        """升级用户会员"""
        user.membership_level = level
        
        # 计算过期时间
        if user.membership_expire_at and user.membership_expire_at > datetime.now():
            # 在现有基础上叠加
            user.membership_expire_at += timedelta(days=days)
        else:
            # 从现在开始计算
            user.membership_expire_at = datetime.now() + timedelta(days=days)
        
        self.db.commit()
        return user
    
    def grant_new_user_trial(self, user: User) -> User:
        """授予新用户 VIP 试用权益（1 天）"""
        return self.upgrade_membership(user, MembershipLevel.VIP.value, days=1)
    
    def get_user_features(self, user: User) -> Dict:
        """获取用户所有功能权限"""
        level_config = self.get_level_config(user.membership_level)
        
        # 检查会员是否有效
        is_valid = self.is_membership_valid(user)
        
        return {
            "level": user.membership_level,
            "level_name": level_config["name"],
            "is_valid": is_valid,
            "expire_at": user.membership_expire_at.isoformat() if user.membership_expire_at else None,
            "permissions": level_config["permissions"],
            "features": level_config["features"],
            "limits": {
                "max_accounts": level_config["max_accounts"],
                "daily_api_limit": level_config["daily_api_limit"],
            },
            "usage": {
                "today_api_calls": user.today_api_calls,
                "total_api_calls": user.total_api_calls,
            }
        }

class AdminService:
    """管理员服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.membership_service = MembershipService(db)
    
    def is_admin(self, user: User) -> bool:
        """检查是否为管理员"""
        return user.role in ["admin", "super_admin"]
    
    def is_super_admin(self, user: User) -> bool:
        """检查是否为超级管理员"""
        return user.role == "super_admin"
    
    def log_operation(self, admin: User, operation: str, target_user: Optional[User] = None, details: dict = None):
        """记录管理员操作日志"""
        from app.models.user import AdminOperationLog
        
        log = AdminOperationLog(
            admin_id=admin.id,
            admin_username=admin.username,
            operation=operation,
            target_user_id=target_user.id if target_user else None,
            target_username=target_user.username if target_user else None,
            details=details or {},
            ip_address=""  # 从请求中获取
        )
        self.db.add(log)
        self.db.commit()
    
    def upgrade_user(self, admin: User, target_user: User, level: str, days: int) -> User:
        """管理员升级用户会员"""
        if not self.is_admin(admin):
            raise PermissionError("需要管理员权限")
        
        user = self.membership_service.upgrade_membership(target_user, level, days)
        self.log_operation(admin, "upgrade_membership", target_user, {
            "level": level,
            "days": days
        })
        return user
    
    def ban_user(self, admin: User, target_user: User, reason: str) -> User:
        """封禁用户"""
        if not self.is_admin(admin):
            raise PermissionError("需要管理员权限")
        
        target_user.status = "banned"
        target_user.permissions = target_user.permissions or []
        target_user.permissions.append(f"banned_reason: {reason}")
        
        self.db.commit()
        self.log_operation(admin, "ban_user", target_user, {"reason": reason})
        return target_user
    
    def unban_user(self, admin: User, target_user: User) -> User:
        """解封用户"""
        if not self.is_admin(admin):
            raise PermissionError("需要管理员权限")
        
        target_user.status = "active"
        if target_user.permissions:
            target_user.permissions = [p for p in target_user.permissions if not p.startswith("banned_reason:")]
        
        self.db.commit()
        self.log_operation(admin, "unban_user", target_user)
        return target_user
