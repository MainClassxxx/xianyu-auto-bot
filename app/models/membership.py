"""
会员订单模型
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.models import ModelBase

class MembershipOrder(ModelBase):
    """会员购买订单"""
    __tablename__ = 'membership_orders'
    
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, index=True, nullable=False)  # 订单号
    
    # 用户信息
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    username = Column(String(50), nullable=False)
    
    # 会员信息
    level = Column(String(20), nullable=False)  # vip, svip
    plan = Column(String(50), nullable=False)  # 1_month, 2_months, etc.
    days = Column(Integer, nullable=False)  # 有效期天数
    price = Column(Float, nullable=False)  # 价格
    
    # 支付信息
    payment_method = Column(String(20))  # alipay, wechat
    transaction_id = Column(String(100))  # 支付交易号
    status = Column(String(20), default='pending')  # pending, paid, cancelled, expired
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    paid_at = Column(DateTime, nullable=True)  # 支付时间
    expire_at = Column(DateTime, default=lambda: datetime.now() + timedelta(minutes=30))  # 订单过期时间
    
    # 备注
    remark = Column(Text, default='')

class MembershipGrantLog(ModelBase):
    """会员开通日志（管理员手动开通）"""
    __tablename__ = 'membership_grant_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 管理员信息
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    admin_username = Column(String(50), nullable=False)
    
    # 用户信息
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    username = Column(String(50), nullable=False)
    
    # 会员信息
    level = Column(String(20), nullable=False)  # vip, svip
    days = Column(Integer, nullable=False)
    
    # 原因
    reason = Column(String(500), default='')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
