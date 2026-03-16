"""
自动发货模型
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models import ModelBase

class DeliveryRule(ModelBase):
    """自动发货规则"""
    __tablename__ = 'delivery_rules'
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    
    # 规则信息
    name = Column(String(100), nullable=False)  # 规则名称
    keyword = Column(String(200))  # 关键词匹配
    match_type = Column(String(20), default='contains')  # contains/exact/regex
    
    # 发货内容
    delivery_content = Column(Text, nullable=False)  # 发货内容
    delivery_type = Column(String(20), default='text')  # text/image/file/url
    
    # 库存管理
    stock = Column(Integer, default=-1)  # 库存数量（-1 为无限）
    auto_restock = Column(Boolean, default=False)  # 自动补货
    
    # 状态
    enabled = Column(Boolean, default=True)  # 是否启用
    priority = Column(Integer, default=0)  # 优先级（数字越大优先级越高）
    
    # 统计
    total_delivered = Column(Integer, default=0)  # 累计发货数
    today_delivered = Column(Integer, default=0)  # 今日发货数
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class DeliveryRecord(ModelBase):
    """发货记录"""
    __tablename__ = 'delivery_records'
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    rule_id = Column(Integer, ForeignKey('delivery_rules.id'))
    
    # 订单信息
    order_id = Column(String(50), nullable=False, index=True)  # 闲鱼订单 ID
    order_no = Column(String(50))  # 订单号
    item_title = Column(String(500))  # 商品标题
    buyer_name = Column(String(100))  # 买家名称
    
    # 发货信息
    delivery_content = Column(Text)  # 实际发货内容
    delivery_type = Column(String(20))  # 发货类型
    delivery_status = Column(String(20), default='pending')  # pending/success/failed
    
    # 错误信息
    error_message = Column(Text)  # 错误信息
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, index=True)
    delivered_at = Column(DateTime, nullable=True)  # 发货时间

class AutoDeliveryLog(ModelBase):
    """自动发货日志"""
    __tablename__ = 'auto_delivery_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    
    # 日志信息
    level = Column(String(20), default='INFO')  # INFO/WARNING/ERROR
    action = Column(String(50))  # 操作类型
    message = Column(Text)  # 日志内容
    
    # 关联数据
    order_id = Column(String(50))  # 订单 ID
    rule_id = Column(Integer)  # 规则 ID
    data = Column(JSON)  # 附加数据
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now, index=True)
