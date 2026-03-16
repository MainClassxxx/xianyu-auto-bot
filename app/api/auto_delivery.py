"""
自动发货 API
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.models.auto_delivery import DeliveryRule, DeliveryRecord, AutoDeliveryLog
from app.services.auto_delivery_service import AutoDeliveryService, DeliveryRuleService
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/auto-delivery", tags=["自动发货"])

class DeliveryRuleCreate(BaseModel):
    """创建发货规则"""
    name: str
    keyword: Optional[str] = None
    match_type: str = "contains"
    delivery_content: str
    delivery_type: str = "text"
    stock: int = -1
    enabled: bool = True
    priority: int = 0

class DeliveryRuleUpdate(BaseModel):
    """更新发货规则"""
    name: Optional[str] = None
    keyword: Optional[str] = None
    delivery_content: Optional[str] = None
    stock: Optional[int] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = None

class DeliveryRuleResponse(BaseModel):
    """发货规则响应"""
    id: int
    name: str
    keyword: Optional[str]
    match_type: str
    delivery_content: str
    delivery_type: str
    stock: int
    enabled: bool
    priority: int
    total_delivered: int
    today_delivered: int

@router.get("/rules", response_model=List[DeliveryRuleResponse])
async def get_delivery_rules(
    account_id: Optional[int] = None,
    enabled: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取发货规则列表"""
    service = DeliveryRuleService(db)
    
    # 获取规则（需要账号管理权限）
    rules = service.get_rules(account_id)
    
    # 过滤启用状态
    if enabled is not None:
        rules = [r for r in rules if r.enabled == enabled]
    
    return rules

@router.post("/rules", response_model=DeliveryRuleResponse)
async def create_delivery_rule(
    rule: DeliveryRuleCreate,
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建发货规则"""
    service = DeliveryRuleService(db)
    
    rule_data = rule.dict()
    rule_data['account_id'] = account_id
    
    new_rule = service.create_rule(rule_data)
    
    return new_rule

@router.put("/rules/{rule_id}", response_model=DeliveryRuleResponse)
async def update_delivery_rule(
    rule_id: int,
    rule_update: DeliveryRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新发货规则"""
    service = DeliveryRuleService(db)
    
    updated_rule = service.update_rule(rule_id, rule_update.dict(exclude_unset=True))
    if not updated_rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return updated_rule

@router.delete("/rules/{rule_id}")
async def delete_delivery_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除发货规则"""
    service = DeliveryRuleService(db)
    
    success = service.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return {"success": True}

@router.post("/rules/{rule_id}/toggle")
async def toggle_delivery_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """启用/禁用规则"""
    service = DeliveryRuleService(db)
    
    rule = service.toggle_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return rule

@router.post("/rules/{rule_id}/stock")
async def update_rule_stock(
    rule_id: int,
    stock: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新库存"""
    service = DeliveryRuleService(db)
    
    rule = service.reset_stock(rule_id, stock)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return {"success": True, "new_stock": stock}

@router.get("/records")
async def get_delivery_records(
    account_id: int,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取发货记录"""
    query = db.query(DeliveryRecord).filter(
        DeliveryRecord.account_id == account_id
    )
    
    if status:
        query = query.filter(DeliveryRecord.delivery_status == status)
    
    query = query.order_by(DeliveryRecord.created_at.desc())
    
    total = query.count()
    records = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "records": records
    }

@router.get("/logs")
async def get_delivery_logs(
    account_id: int,
    level: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取发货日志"""
    query = db.query(AutoDeliveryLog).filter(
        AutoDeliveryLog.account_id == account_id
    )
    
    if level:
        query = query.filter(AutoDeliveryLog.level == level)
    
    query = query.order_by(AutoDeliveryLog.created_at.desc())
    
    total = query.count()
    logs = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total,
        "logs": logs
    }

@router.post("/trigger")
async def trigger_auto_delivery(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """手动触发自动发货"""
    service = AutoDeliveryService(db)
    
    # TODO: 需要实现真实的闲鱼 API 客户端
    # 这里先返回模拟结果
    return {
        "success": True,
        "message": "自动发货已触发",
        "delivered_count": 0  # 实际发货数量
    }
