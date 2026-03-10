"""
自动发货 API
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/auto-delivery", tags=["自动发货"])

class DeliveryRule(BaseModel):
    name: str
    item_id: Optional[str] = None
    keyword: Optional[str] = None
    delivery_content: str
    delivery_type: str = "text"  # text/file/api
    stock: int = -1  # -1 为无限
    enabled: bool = True

class DeliveryRuleResponse(DeliveryRule):
    id: int

@router.get("/rules", response_model=List[DeliveryRuleResponse])
async def get_delivery_rules(account_id: Optional[int] = None):
    """获取自动发货规则列表"""
    return []

@router.post("/rules", response_model=DeliveryRuleResponse)
async def create_delivery_rule(rule: DeliveryRule):
    """创建自动发货规则"""
    return {"id": 1, **rule.dict()}

@router.put("/rules/{rule_id}")
async def update_delivery_rule(rule_id: int, rule: DeliveryRule):
    """更新自动发货规则"""
    return {"success": True}

@router.delete("/rules/{rule_id}")
async def delete_delivery_rule(rule_id: int):
    """删除自动发货规则"""
    return {"success": True}

@router.get("/stock/{rule_id}")
async def get_stock(rule_id: int):
    """查询库存"""
    return {"rule_id": rule_id, "stock": 100, "used": 50}

@router.post("/stock/{rule_id}/reset")
async def reset_stock(rule_id: int, stock: int):
    """重置库存"""
    return {"success": True}

@router.get("/history")
async def get_delivery_history(page: int = 1, page_size: int = 50):
    """获取发货历史"""
    return {"records": []}
