"""
自动发货服务
"""
from typing import List, Dict, Any
from loguru import logger
from datetime import datetime

class DeliveryService:
    """自动发货服务"""
    
    def __init__(self):
        self.rules = []
        self.delivery_history = []
    
    async def check_and_deliver(self, orders: List[Dict[str, Any]]) -> int:
        """检查并执行自动发货"""
        delivered_count = 0
        
        for order in orders:
            if await self.should_deliver(order):
                success = await self.execute_delivery(order)
                if success:
                    delivered_count += 1
                    logger.info(f"✅ 订单 {order['id']} 自动发货成功")
                else:
                    logger.error(f"❌ 订单 {order['id']} 自动发货失败")
        
        return delivered_count
    
    async def should_deliver(self, order: Dict[str, Any]) -> bool:
        """判断是否应该发货"""
        # 检查订单状态
        if order.get("status") != "paid":
            return False
        
        # 匹配发货规则
        for rule in self.rules:
            if self.match_rule(order, rule):
                return True
        
        return False
    
    def match_rule(self, order: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """匹配发货规则"""
        # 关键词匹配
        keyword = rule.get("keyword", "")
        item_name = order.get("item_name", "")
        
        if keyword and keyword in item_name:
            return True
        
        return False
    
    async def execute_delivery(self, order: Dict[str, Any]) -> bool:
        """执行发货"""
        try:
            # 这里调用闲鱼 API 执行实际发货
            # 目前是模拟实现
            self.delivery_history.append({
                "order_id": order["id"],
                "deliver_time": datetime.now().isoformat(),
                "status": "success"
            })
            return True
        except Exception as e:
            logger.error(f"执行发货失败：{e}")
            return False
    
    def add_rule(self, rule: Dict[str, Any]):
        """添加发货规则"""
        self.rules.append(rule)
        logger.info(f"添加发货规则：{rule.get('name')}")
    
    def remove_rule(self, rule_id: int):
        """删除发货规则"""
        self.rules = [r for r in self.rules if r.get("id") != rule_id]
        logger.info(f"删除发货规则：{rule_id}")
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取发货历史"""
        return self.delivery_history[-limit:]
