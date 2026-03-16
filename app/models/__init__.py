"""
数据模型模块 - 使用独立的 Base
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# 独立的 Base（用于模型定义）
ModelBase = declarative_base()

# 导入所有模型（方便统一创建表）
from app.models.user import User, APILog, AdminOperationLog

class Account(ModelBase):
    """闲鱼账号"""
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # 账号备注
    cookie = Column(Text, nullable=False)  # 闲鱼 Cookie
    device_id = Column(String(50), unique=True)  # 设备 ID
    status = Column(String(20), default='active')  # active/inactive/banned
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联
    items = relationship("Item", back_populates="account")
    orders = relationship("Order", back_populates="account")
    messages = relationship("Message", back_populates="account")

class Item(ModelBase):
    """商品"""
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    item_id = Column(String(50), unique=True)  # 闲鱼商品 ID
    title = Column(String(500))  # 标题
    price = Column(Float)  # 价格
    original_price = Column(Float)  # 原价
    status = Column(String(20))  # onsale/sold/out
    images = Column(JSON)  # 图片 URL 列表
    description = Column(Text)  # 描述
    category = Column(String(100))  # 分类
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    account = relationship("Account", back_populates="items")

class Order(ModelBase):
    """订单"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    order_id = Column(String(50), unique=True)  # 闲鱼订单 ID
    buyer_name = Column(String(100))  # 买家名称
    item_title = Column(String(500))  # 商品标题
    price = Column(Float)  # 订单金额
    status = Column(String(20))  # pending/paid/shipped/completed/refunded
    shipping_info = Column(JSON)  # 发货信息
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    account = relationship("Account", back_populates="orders")

class Message(ModelBase):
    """消息"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    conversation_id = Column(String(50))  # 会话 ID
    sender_id = Column(String(50))  # 发送者 ID
    content = Column(Text)  # 消息内容
    msg_type = Column(String(20), default='text')  # text/image
    image_url = Column(String(500))  # 图片 URL
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    account = relationship("Account", back_populates="messages")

class AutoReplyRule(ModelBase):
    """自动回复规则"""
    __tablename__ = 'auto_reply_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    name = Column(String(100))  # 规则名称
    keyword = Column(String(200))  # 关键词
    match_type = Column(String(20), default='contains')  # exact/contains/regex/ai
    reply_content = Column(Text)  # 回复内容
    reply_type = Column(String(20), default='text')  # text/image
    image_url = Column(String(500))  # 回复图片
    enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # 优先级
    created_at = Column(DateTime, default=datetime.now)

class DeliveryRule(ModelBase):
    """自动发货规则"""
    __tablename__ = 'delivery_rules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(Integer, ForeignKey('accounts.id'))
    name = Column(String(100))  # 规则名称
    item_id = Column(String(50))  # 商品 ID（可选）
    keyword = Column(String(200))  # 关键词
    delivery_content = Column(Text)  # 发货内容
    delivery_type = Column(String(20), default='text')  # text/file/api
    stock = Column(Integer, default=-1)  # 库存（-1 为无限）
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class NotificationChannel(ModelBase):
    """通知渠道"""
    __tablename__ = 'notification_channels'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))  # 渠道名称
    channel_type = Column(String(20))  # feishu/telegram/wechat/dingtalk
    webhook_url = Column(Text)  # Webhook URL
    token = Column(String(200))  # Token
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

class SystemLog(ModelBase):
    """系统日志"""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20))  # INFO/WARNING/ERROR
    module = Column(String(50))  # 模块名称
    message = Column(Text)  # 日志内容
    data = Column(JSON)  # 附加数据
    created_at = Column(DateTime, default=datetime.now, index=True)
