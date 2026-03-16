"""
推广返利模型
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models import ModelBase

class ReferralStatus(enum.Enum):
    """推广状态"""
    PENDING = "pending"      # 待生效
    ACTIVE = "active"        # 已生效（用户已购买）
    EXPIRED = "expired"      # 已过期

class ReferralLink(ModelBase):
    """推广链接"""
    __tablename__ = 'referral_links'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    username = Column(String(50), nullable=False)
    
    # 推广码（唯一）
    referral_code = Column(String(20), unique=True, nullable=False, index=True)
    
    # 推广链接
    referral_url = Column(String(500), nullable=False)
    
    # 统计信息
    total_clicks = Column(Integer, default=0)  # 总点击数
    total_registrations = Column(Integer, default=0)  # 总注册数
    total_purchases = Column(Integer, default=0)  # 总购买数
    total_earnings = Column(Float, default=0.0)  # 总收益
    
    # 状态
    is_active = Column(Boolean, default=True)  # 是否启用
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    referrals = relationship("ReferralRecord", back_populates="referral_link", foreign_keys="ReferralRecord.referral_link_id")

class ReferralRecord(ModelBase):
    """推广记录（每次注册/购买）"""
    __tablename__ = 'referral_records'
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 推广链接 ID
    referral_link_id = Column(Integer, ForeignKey('referral_links.id'), nullable=False)
    
    # 推广人信息
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    referrer_username = Column(String(50), nullable=False)
    
    # 被推广人信息
    referred_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    referred_username = Column(String(50), nullable=True)
    
    # 订单信息
    order_no = Column(String(50), nullable=True)  # 购买的订单号
    order_amount = Column(Float, default=0.0)  # 订单金额
    
    # 返利信息
    commission_rate = Column(Float, default=0.3)  # 返利比例（30%）
    commission_amount = Column(Float, default=0.0)  # 返利金额
    status = Column(String(20), default=ReferralStatus.PENDING.value)  # 状态
    
    # 时间戳
    registered_at = Column(DateTime, nullable=True)  # 注册时间
    purchased_at = Column(DateTime, nullable=True)  # 购买时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 关联
    referral_link = relationship("ReferralLink", back_populates="referrals")

class UserBalance(ModelBase):
    """用户余额"""
    __tablename__ = 'user_balances'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False, index=True)
    username = Column(String(50), nullable=False)
    
    # 余额
    balance = Column(Float, default=0.0)  # 可用余额
    frozen_balance = Column(Float, default=0.0)  # 冻结余额
    total_recharge = Column(Float, default=0.0)  # 总充值
    total_consumption = Column(Float, default=0.0)  # 总消费
    total_commission = Column(Float, default=0.0)  # 总返利
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    transactions = relationship("BalanceTransaction", back_populates="user_balance")

class BalanceTransaction(ModelBase):
    """余额交易记录"""
    __tablename__ = 'balance_transactions'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_balances.user_id'), nullable=False, index=True)
    
    # 交易类型
    transaction_type = Column(String(20), nullable=False)  # recharge, commission, consumption, withdraw
    # recharge: 充值
    # commission: 返利
    # consumption: 消费
    # withdraw: 提现
    
    # 金额
    amount = Column(Float, nullable=False)  # 交易金额（正数）
    balance_before = Column(Float, nullable=False)  # 交易前余额
    balance_after = Column(Float, nullable=False)  # 交易后余额
    
    # 关联信息
    related_order_no = Column(String(50))  # 相关订单号
    related_referral_id = Column(Integer)  # 相关推广记录 ID
    
    # 描述
    description = Column(String(500), default='')
    remark = Column(Text, default='')
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, index=True)

class RechargeOrder(ModelBase):
    """充值订单"""
    __tablename__ = 'recharge_orders'
    
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('user_balances.user_id'), nullable=False)
    username = Column(String(50), nullable=False)
    
    # 充值金额
    amount = Column(Float, nullable=False)
    
    # 支付方式
    payment_method = Column(String(20), nullable=False)  # alipay, wechat
    
    # 状态
    status = Column(String(20), default='pending')  # pending, paid, cancelled
    
    # 支付信息
    transaction_id = Column(String(100))  # 支付交易号
    paid_at = Column(DateTime, nullable=True)  # 支付时间
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    expire_at = Column(DateTime, default=lambda: datetime.now() + timedelta(minutes=30))  # 订单过期时间
