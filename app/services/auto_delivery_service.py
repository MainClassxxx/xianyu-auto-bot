"""
自动发货服务 - 完整实现
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session
from app.models import Order, DeliveryRule, SystemLog
from app.services.xianyu_api import XianyuClient

class AutoDeliveryService:
    """自动发货服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def check_and_deliver(self, account_id: int, client: XianyuClient) -> int:
        """检查并执行自动发货"""
        delivered_count = 0
        
        try:
            # 1. 获取待发货订单
            orders = await client.get_orders(status="paid")
            logger.info(f"📦 获取到 {len(orders)} 个已付款订单")
            
            # 2. 获取自动发货规则
            rules = self.db.query(DeliveryRule).filter(
                DeliveryRule.account_id == account_id,
                DeliveryRule.enabled == True
            ).all()
            
            if not rules:
                logger.warning(f"⚠️ 账号 {account_id} 没有配置自动发货规则")
                return 0
            
            # 3. 遍历订单，匹配规则并发货
            for order in orders:
                success = await self.process_order(order, rules, client)
                if success:
                    delivered_count += 1
            
            logger.info(f"✅ 完成自动发货，共发货 {delivered_count} 单")
            
        except Exception as e:
            logger.error(f"❌ 自动发货失败：{e}")
        
        return delivered_count
    
    async def process_order(self, order: Dict[str, Any], rules: List[DeliveryRule], client: XianyuClient) -> bool:
        """处理单个订单"""
        try:
            order_id = order.get("orderId")
            item_title = order.get("itemTitle", "")
            buyer_id = order.get("buyerId")
            
            # 1. 匹配发货规则
            matched_rule = None
            for rule in rules:
                if self.match_rule(item_title, rule):
                    matched_rule = rule
                    break
            
            if not matched_rule:
                logger.warning(f"⚠️ 订单 {order_id} 没有匹配的发货规则")
                return False
            
            # 2. 检查库存
            if matched_rule.stock != -1:
                if matched_rule.stock <= 0:
                    logger.warning(f"⚠️ 规则 {matched_rule.name} 库存不足")
                    return False
            
            # 3. 执行发货
            delivery_content = matched_rule.delivery_content
            success = await client.deliver_order(order_id, delivery_content)
            
            if success:
                # 4. 扣减库存
                if matched_rule.stock != -1:
                    matched_rule.stock -= 1
                    self.db.commit()
                
                # 5. 记录日志
                self.log_delivery(order_id, matched_rule.id, "success")
                
                logger.info(f"✅ 订单 {order_id} 自动发货成功")
                return True
            else:
                self.log_delivery(order_id, matched_rule.id, "failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ 处理订单失败：{e}")
            return False
    
    def match_rule(self, item_title: str, rule: DeliveryRule) -> bool:
        """匹配发货规则"""
        if not rule.keyword:
            return True
        
        keyword = rule.keyword.lower()
        title = item_title.lower()
        
        return keyword in title
    
    def log_delivery(self, order_id: str, rule_id: int, status: str):
        """记录发货日志"""
        log = SystemLog(
            level="INFO",
            module="auto_delivery",
            message=f"订单 {order_id} 发货 {'成功' if status == 'success' else '失败'}",
            data={
                "order_id": order_id,
                "rule_id": rule_id,
                "status": status
            }
        )
        self.db.add(log)
        self.db.commit()


class DeliveryRuleService:
    """发货规则服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_rules(self, account_id: Optional[int] = None) -> List[DeliveryRule]:
        """获取发货规则列表"""
        query = self.db.query(DeliveryRule)
        if account_id:
            query = query.filter(DeliveryRule.account_id == account_id)
        return query.all()
    
    def create_rule(self, rule_data: Dict[str, Any]) -> DeliveryRule:
        """创建发货规则"""
        rule = DeliveryRule(**rule_data)
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        logger.info(f"✅ 创建发货规则：{rule.name}")
        return rule
    
    def update_rule(self, rule_id: int, update_data: Dict[str, Any]) -> Optional[DeliveryRule]:
        """更新发货规则"""
        rule = self.db.query(DeliveryRule).filter(DeliveryRule.id == rule_id).first()
        if rule:
            for key, value in update_data.items():
                if hasattr(rule, key):
                    setattr(rule, key, value)
            self.db.commit()
            self.db.refresh(rule)
            logger.info(f"✅ 更新发货规则：{rule.name}")
            return rule
        return None
    
    def delete_rule(self, rule_id: int) -> bool:
        """删除发货规则"""
        rule = self.db.query(DeliveryRule).filter(DeliveryRule.id == rule_id).first()
        if rule:
            self.db.delete(rule)
            self.db.commit()
            logger.info(f"✅ 删除发货规则：{rule.name}")
            return True
        return False
    
    def toggle_rule(self, rule_id: int) -> Optional[DeliveryRule]:
        """启用/禁用规则"""
        rule = self.db.query(DeliveryRule).filter(DeliveryRule.id == rule_id).first()
        if rule:
            rule.enabled = not rule.enabled
            self.db.commit()
            logger.info(f"✅ 规则 {rule.name} 已{'启用' if rule.enabled else '禁用'}")
            return rule
        return None
    
    def reset_stock(self, rule_id: int, stock: int) -> Optional[DeliveryRule]:
        """重置库存"""
        rule = self.db.query(DeliveryRule).filter(DeliveryRule.id == rule_id).first()
        if rule:
            rule.stock = stock
            self.db.commit()
            logger.info(f"✅ 规则 {rule.name} 库存重置为 {stock}")
            return rule
        return None
