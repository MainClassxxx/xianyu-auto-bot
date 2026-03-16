"""
用户模型 - 扩展会员等级系统
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import enum
from . import ModelBase

class MembershipLevel(enum.Enum):
    """会员等级"""
    NORMAL = "normal"      # 普通用户
    VIP = "vip"           # VIP 用户
    SVIP = "svip"         # SVIP 用户

class User(ModelBase):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 基本信息
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avatar = Column(String(255), default="")
    phone = Column(String(20), default="")
    
    # 角色和等级
    role = Column(String(20), default="user")  # user, admin, super_admin
    membership_level = Column(String(20), default="normal")  # normal, vip, svip
    
    # 会员有效期
    membership_expire_at = Column(DateTime, nullable=True)  # 会员过期时间
    
    # 账号状态
    status = Column(String(20), default="active")  # active, inactive, banned
    
    # 权益相关
    agree_terms = Column(Boolean, default=False)
    
    # 使用统计
    total_api_calls = Column(Integer, default=0)  # 总 API 调用次数
    today_api_calls = Column(Integer, default=0)  # 今日 API 调用次数
    last_api_call_at = Column(DateTime, nullable=True)  # 最后 API 调用时间
    
    # 额外权限 (JSON 格式存储特殊权限)
    permissions = Column(JSON, default=list)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    last_login_at = Column(DateTime, nullable=True)
    
    # 关联
    accounts = relationship("Account", back_populates="user")
    api_logs = relationship("APILog", back_populates="user")

class APILog(ModelBase):
    """API 调用日志"""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    endpoint = Column(String(200))  # API 端点
    method = Column(String(10))  # GET, POST, etc.
    status_code = Column(Integer)  # HTTP 状态码
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.now, index=True)
    
    # 关联
    user = relationship("User", back_populates="api_logs")

class AdminOperationLog(ModelBase):
    """管理员操作日志"""
    __tablename__ = "admin_operation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, index=True)
    admin_username = Column(String(50))
    operation = Column(String(100))  # 操作类型
    target_user_id = Column(Integer, nullable=True)  # 目标用户 ID
    target_username = Column(String(50), nullable=True)
    details = Column(JSON, default=dict)  # 操作详情
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.now, index=True)
