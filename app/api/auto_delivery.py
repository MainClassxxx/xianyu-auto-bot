"""
自动发货 API - 真实实现
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import DeliveryRule
from app.services.auto_delivery_service import DeliveryRuleService

router = APIRouter(prefix="/api/auto-delivery", tags=["自动发货"])

class DeliveryRuleCreate(BaseModel):
    account_id: int
    name: str
    keyword: Optional[str] = None
    delivery_content: str
    delivery_type: str = "text"
    stock: int = -1
    enabled: bool = True

class DeliveryRuleUpdate(BaseModel):
    name: Optional[str] = None
    keyword: Optional[str] = None
    delivery_content: Optional[str] = None
    stock: Optional[int] = None
    enabled: Optional[bool] = None

@router.get("/rules", response_model=List[dict])
async def get_delivery_rules(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """获取自动发货规则列表"""
    service = DeliveryRuleService(db)
    rules = service.get_rules(account_id)
    return rules

@router.post("/rules", response_model=dict)
async def create_delivery_rule(
    rule: DeliveryRuleCreate,
    db: Session = Depends(get_db)
):
    """创建自动发货规则"""
    service = DeliveryRuleService(db)
    rule_data = rule.dict()
    new_rule = service.create_rule(rule_data)
    return new_rule

@router.put("/rules/{rule_id}")
async def update_delivery_rule(
    rule_id: int,
    rule_update: DeliveryRuleUpdate,
    db: Session = Depends(get_db)
):
    """更新自动发货规则"""
    service = DeliveryRuleService(db)
    updated_rule = service.update_rule(rule_id, rule_update.dict(exclude_unset=True))
    if not updated_rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return updated_rule

@router.delete("/rules/{rule_id}")
async def delete_delivery_rule(rule_id: int, db: Session = Depends(get_db)):
    """删除自动发货规则"""
    service = DeliveryRuleService(db)
    success = service.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="规则不存在")
    return {"success": True}

@router.post("/rules/{rule_id}/toggle")
async def toggle_delivery_rule(rule_id: int, db: Session = Depends(get_db)):
    """启用/禁用规则"""
    service = DeliveryRuleService(db)
    rule = service.toggle_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return rule

@router.get("/stock/{rule_id}")
async def get_stock(rule_id: int, db: Session = Depends(get_db)):
    """查询库存"""
    rule = db.query(DeliveryRule).filter(DeliveryRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return {"rule_id": rule_id, "stock": rule.stock, "used": 0}

@router.post("/stock/{rule_id}/reset")
async def reset_stock(
    rule_id: int,
    stock: int,
    db: Session = Depends(get_db)
):
    """重置库存"""
    service = DeliveryRuleService(db)
    rule = service.reset_stock(rule_id, stock)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return {"success": True, "new_stock": stock}

@router.get("/history")
async def get_delivery_history(
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    """获取发货历史"""
    # TODO: 实现发货历史查询
    return {"records": []}
