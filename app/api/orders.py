"""
订单管理 API - 真实实现
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Order
from app.services.xianyu_api import xianyu_manager

router = APIRouter(prefix="/api/orders", tags=["订单管理"])

class DeliverRequest(BaseModel):
    content: str

@router.get("", response_model=List[dict])
async def get_orders(
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取订单列表"""
    if account_id:
        account = db.query(Account).filter(Account.id == account_id).first()
        if not account:
            raise HTTPException(status_code=404, detail="账号不存在")
        
        client = xianyu_manager.get_client(str(account_id))
        if not client:
            raise HTTPException(status_code=400, detail="账号未连接")
        
        orders = await client.get_orders(status=status or "all", page=page, page_size=page_size)
        return orders
    
    # 返回所有账号的订单
    return []

@router.get("/{order_id}")
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """获取订单详情"""
    # TODO: 实现订单详情
    return {"order_id": order_id}

@router.post("/{order_id}/deliver")
async def deliver_order(
    order_id: str,
    deliver_req: DeliverRequest,
    account_id: int,
    db: Session = Depends(get_db)
):
    """发货"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="账号不存在")
    
    client = xianyu_manager.get_client(str(account_id))
    if not client:
        raise HTTPException(status_code=400, detail="账号未连接")
    
    success = await client.deliver_order(order_id, deliver_req.content)
    
    if success:
        return {"success": True, "message": "发货成功"}
    else:
        raise HTTPException(status_code=500, detail="发货失败")

@router.post("/{order_id}/refresh")
async def refresh_order(order_id: str, db: Session = Depends(get_db)):
    """刷新订单状态"""
    # TODO: 实现订单状态刷新
    return {"success": True}

@router.delete("/{order_id}")
async def delete_order(order_id: str, db: Session = Depends(get_db)):
    """删除订单"""
    # TODO: 实现订单删除
    return {"success": True}
